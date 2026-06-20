from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from lebihsini_greenproof.api.dependencies import get_dataset, get_repository
from lebihsini_greenproof.confidence import passport_may_enter_automatic_matching
from lebihsini_greenproof.contracts import EquipmentResourcePassport, MaterialResourcePassport, VerificationStatus
from lebihsini_greenproof.demo_data import DemoDataset
from lebihsini_greenproof.serialization import to_jsonable
from lebihsini_greenproof.repositories.in_memory import InMemoryRepository
from lebihsini_greenproof.services.extraction_service import ServiceError


router = APIRouter(tags=["resources"])


def _automatic_matching_eligible(resource: MaterialResourcePassport | EquipmentResourcePassport) -> bool:
    if isinstance(resource, MaterialResourcePassport):
        return passport_may_enter_automatic_matching(
            resource.confidence,
            resource.verification_status.value,
            resource.inspection_required,
        )
    if resource.verification_status == VerificationStatus.UNVERIFIED:
        return False
    if not resource.maintenance_record_present:
        return False
    return resource.maintenance_confidence >= 0.8


@router.get("/resources")
def list_resources(
    repository: InMemoryRepository = Depends(get_repository),
    dataset: DemoDataset = Depends(get_dataset),
    resource_type: str | None = None,
    material_category: str | None = None,
    equipment_category: str | None = None,
    risk_category: str | None = None,
    verification_status: str | None = None,
    site_id: str | None = None,
    automatic_matching_eligibility: bool | None = Query(default=None),
) -> dict:
    material_resources = list(repository.material_passports.values()) or list(dataset.material_resources)
    equipment_resources = list(repository.equipment_passports.values()) or [
        *dataset.equipment_resources,
        dataset.commercial_equipment_fallback,
    ]
    resources = []
    if resource_type in (None, "material"):
        resources.extend(material_resources)
    if resource_type in (None, "equipment"):
        resources.extend(equipment_resources)
    filtered = []
    for resource in resources:
        if material_category and isinstance(resource, MaterialResourcePassport) and resource.category != material_category:
            continue
        if equipment_category and isinstance(resource, EquipmentResourcePassport) and resource.category != equipment_category:
            continue
        if risk_category and resource.risk_category.value != risk_category:
            continue
        if verification_status and resource.verification_status.value != verification_status:
            continue
        if site_id and resource.site_id != site_id:
            continue
        eligible = _automatic_matching_eligible(resource)
        if automatic_matching_eligibility is not None and eligible != automatic_matching_eligibility:
            continue
        payload = to_jsonable(resource)
        payload["resource_type"] = "material" if isinstance(resource, MaterialResourcePassport) else "equipment"
        payload["automatic_matching_eligibility"] = eligible
        filtered.append(payload)
    return {"items": filtered, "storage_mode": "in_memory", "count": len(filtered)}


@router.get("/resources/{resource_id}")
def get_resource(
    resource_id: str,
    repository: InMemoryRepository = Depends(get_repository),
    dataset: DemoDataset = Depends(get_dataset),
) -> dict:
    all_resources = {
        resource.resource_id: resource for resource in dataset.material_resources
    } | {
        resource.resource_id: resource for resource in dataset.equipment_resources
    } | {
        dataset.commercial_equipment_fallback.resource_id: dataset.commercial_equipment_fallback
    } | repository.material_passports | repository.equipment_passports
    resource = all_resources.get(resource_id)
    if resource is None:
        raise ServiceError("RESOURCE_NOT_FOUND", "Resource was not found.", status_code=404)
    payload = to_jsonable(resource)
    payload["resource_type"] = "material" if isinstance(resource, MaterialResourcePassport) else "equipment"
    payload["automatic_matching_eligibility"] = _automatic_matching_eligible(resource)
    return payload
