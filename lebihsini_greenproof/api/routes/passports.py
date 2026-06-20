from __future__ import annotations

from dataclasses import replace

from fastapi import APIRouter, Depends

from lebihsini_greenproof.api.dependencies import get_extraction_service
from lebihsini_greenproof.api.models import EquipmentPassportBody, MaterialPassportBody
from lebihsini_greenproof.contracts import AIExtractionRequest
from lebihsini_greenproof.serialization import to_jsonable
from lebihsini_greenproof.services.extraction_service import ExtractionService


router = APIRouter(tags=["passports"])


@router.post("/material-passports")
def create_material_passport(
    body: MaterialPassportBody,
    service: ExtractionService = Depends(get_extraction_service),
) -> dict:
    request = AIExtractionRequest(**body.model_dump(exclude={"resource_id", "human_confirmed_quantity_units"}))
    result = service.create_material_passport(request, body.resource_id, body.human_confirmed_quantity_units)
    return to_jsonable(result)


@router.post("/equipment-passports")
def create_equipment_passport(
    body: EquipmentPassportBody,
    service: ExtractionService = Depends(get_extraction_service),
) -> dict:
    request = AIExtractionRequest(**body.model_dump(exclude={"resource_id"}))
    result = service.create_equipment_passport(request, body.resource_id)
    return to_jsonable(result)
