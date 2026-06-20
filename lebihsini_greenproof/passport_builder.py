from __future__ import annotations

from dataclasses import replace

from lebihsini_greenproof.confidence import passport_may_enter_automatic_matching
from lebihsini_greenproof.contracts import (
    MaterialResourcePassport,
    PassportGenerationResult,
    ProcessingWarning,
    ResourceKind,
    ResourceScanExtractionResult,
    RiskCategory,
    VerificationStatus,
    EquipmentResourcePassport,
)
from lebihsini_greenproof.explanations import EXPLANATION_TEXT


def build_material_passport(
    extraction_result: ResourceScanExtractionResult,
    base_passport: MaterialResourcePassport,
    human_confirmed_quantity_units: int | None = None,
) -> PassportGenerationResult:
    data = extraction_result.normalized_resource_data
    product_code = data.get("product_code") or base_passport.product_code
    storage_condition = data.get("storage_condition") or base_passport.storage_condition
    risk_category = base_passport.risk_category
    verification_status = base_passport.verification_status
    inspection_required = base_passport.inspection_required
    warnings = list(extraction_result.warnings)
    if product_code in (None, "", "UNKNOWN") or storage_condition == "outdoor_exposed":
        risk_category = RiskCategory.RED
        verification_status = VerificationStatus.UNVERIFIED
        inspection_required = True
        warnings.append(
            ProcessingWarning(
                code="MANUAL_INSPECTION_REQUIRED",
                message=EXPLANATION_TEXT["site_e_uncertainty"],
                field_name="product_code",
            )
        )
    passport = replace(
        base_passport,
        brand=data.get("brand") or base_passport.brand,
        product_code=product_code or base_passport.product_code,
        dimension_mm_width=data.get("dimension_mm_width") or base_passport.dimension_mm_width,
        dimension_mm_height=data.get("dimension_mm_height") or base_passport.dimension_mm_height,
        colour=data.get("colour") or base_passport.colour,
        quantity_estimate_units=data.get("quantity_estimate_units") or base_passport.quantity_units,
        human_confirmed_quantity_units=human_confirmed_quantity_units,
        batch_number=data.get("batch_number"),
        packaging_status=data.get("packaging_status") or base_passport.packaging_status,
        storage_condition=storage_condition,
        exposure_information=data.get("storage_condition"),
        risk_category=risk_category,
        verification_status=verification_status,
        inspection_required=inspection_required,
        has_required_documentation=product_code not in (None, "", "UNKNOWN"),
        evidence_notes=base_passport.evidence_notes + [item.message for item in warnings],
    )
    return PassportGenerationResult(
        request_id=extraction_result.request_id,
        resource_kind=ResourceKind.MATERIAL,
        can_enter_automatic_matching=passport_may_enter_automatic_matching(
            passport.confidence,
            passport.verification_status.value,
            passport.inspection_required,
        ),
        requires_manual_review=passport.inspection_required,
        warnings=warnings,
        generated_material_passport=passport,
    )


def build_equipment_passport(
    extraction_result: ResourceScanExtractionResult,
    base_passport: EquipmentResourcePassport,
) -> PassportGenerationResult:
    data = extraction_result.normalized_resource_data
    warnings = list(extraction_result.warnings)
    maintenance_record_present = bool(data.get("maintenance_record_present", base_passport.maintenance_record_present))
    inspection_required = not maintenance_record_present or base_passport.maintenance_confidence < 0.8
    if inspection_required:
        warnings.append(
            ProcessingWarning(
                code="MANUAL_INSPECTION_REQUIRED",
                message="Equipment maintenance evidence is incomplete and requires manual review.",
                field_name="maintenance_record_present",
            )
        )
    passport = replace(
        base_passport,
        brand_model=data.get("brand_model") or base_passport.brand_model,
        capacity=data.get("capacity") or base_passport.capacity,
        maintenance_date_at=data.get("maintenance_date_at") or base_passport.maintenance_date_at,
        maintenance_record_present=maintenance_record_present,
        operator_required=bool(data.get("operator_required", base_passport.operator_required)),
        visible_condition=data.get("visible_condition") or base_passport.visible_condition,
        evidence_notes=base_passport.evidence_notes + [item.message for item in warnings],
    )
    return PassportGenerationResult(
        request_id=extraction_result.request_id,
        resource_kind=ResourceKind.EQUIPMENT,
        can_enter_automatic_matching=not inspection_required,
        requires_manual_review=inspection_required,
        warnings=warnings,
        generated_equipment_passport=passport,
    )
