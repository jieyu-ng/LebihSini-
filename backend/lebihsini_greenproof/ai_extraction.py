from __future__ import annotations

from dataclasses import dataclass

from lebihsini_greenproof.ai_provider import AIProvider, AIProviderException
from lebihsini_greenproof.composer import generate_recommendation
from lebihsini_greenproof.confidence import identify_missing_critical_fields
from lebihsini_greenproof.contracts import (
    AIExtractionRequest,
    ConfidenceLabel,
    ConfirmationAction,
    ConfirmationStatus,
    ConfirmedFieldValue,
    DemandRequest,
    ProcessingWarning,
    ResourceKind,
    RiskCategory,
    StructuredDemandExtractionResult,
    UserConfirmedExtraction,
)
from lebihsini_greenproof.demo_data import DemoDataset
from lebihsini_greenproof.input_processing import normalize_language_code
from lebihsini_greenproof.passport_builder import build_equipment_passport, build_material_passport
from lebihsini_greenproof.structured_output import (
    validate_demand_provider_output,
    validate_resource_provider_output,
)


@dataclass(slots=True)
class ConfirmationInput:
    request_id: str
    action: ConfirmationAction
    confirmed_values: dict[str, object]
    confirmed_at: str


def extract_demand(
    request: AIExtractionRequest,
    provider: AIProvider,
) -> StructuredDemandExtractionResult:
    response = provider.extract_demand(request)
    return validate_demand_provider_output(request, response.payload)


def confirm_demand_extraction(
    extraction_result: StructuredDemandExtractionResult,
    confirmation: ConfirmationInput,
) -> UserConfirmedExtraction:
    if confirmation.action in {ConfirmationAction.REJECT, ConfirmationAction.RETAKE, ConfirmationAction.MANUAL_REVIEW}:
        return UserConfirmedExtraction(
            request_id=extraction_result.request_id,
            status={
                ConfirmationAction.REJECT: ConfirmationStatus.REJECTED,
                ConfirmationAction.RETAKE: ConfirmationStatus.RETAKE_REQUESTED,
                ConfirmationAction.MANUAL_REVIEW: ConfirmationStatus.MANUAL_REVIEW,
            }[confirmation.action],
            confirmed_fields=[],
            warnings=extraction_result.warnings,
            confirmed_demand=None,
        )

    confirmed_field_values: list[ConfirmedFieldValue] = []
    confirmed_data = dict(extraction_result.normalized_demand)
    for field in extraction_result.extracted_fields:
        confirmed_value = confirmation.confirmed_values.get(field.field_name, field.extracted_value)
        confirmed_field_values.append(
            ConfirmedFieldValue(
                field_name=field.field_name,
                extracted_value=field.extracted_value,
                confirmed_value=confirmed_value,
                confidence_score=field.confidence_score,
                confidence_label=field.confidence_label,
                confirmation_action=ConfirmationAction.EDIT if confirmed_value != field.extracted_value else ConfirmationAction.ACCEPT,
                confirmed_at=confirmation.confirmed_at,
            )
        )
        confirmed_data[field.field_name] = confirmed_value
    for field_name, value in confirmation.confirmed_values.items():
        if field_name not in {item.field_name for item in extraction_result.extracted_fields}:
            confirmed_field_values.append(
                ConfirmedFieldValue(
                    field_name=field_name,
                    extracted_value=None,
                    confirmed_value=value,
                    confidence_score=1.0,
                    confidence_label=ConfidenceLabel.HIGH,
                    confirmation_action=ConfirmationAction.PROVIDE,
                    confirmed_at=confirmation.confirmed_at,
                )
            )
            confirmed_data[field_name] = value

    remaining_missing = identify_missing_critical_fields(confirmed_data)
    if remaining_missing:
        return UserConfirmedExtraction(
            request_id=extraction_result.request_id,
            status=ConfirmationStatus.MANUAL_REVIEW,
            confirmed_fields=confirmed_field_values,
            warnings=extraction_result.warnings
            + [
                ProcessingWarning(
                    code="MISSING_CRITICAL_FIELD",
                    message=item.message,
                    field_name=item.field_name,
                )
                for item in remaining_missing
            ],
            confirmed_demand=None,
        )

    demand = DemandRequest(
        demand_id=f"demand-confirmed-{extraction_result.request_id}",
        requesting_site_id="site-c",
        material_category=str(confirmed_data["material_category"]),
        product_code=str(confirmed_data.get("product_code") or "UNKNOWN"),
        colour=str(confirmed_data.get("colour") or "grey"),
        dimension_mm_width=int(confirmed_data["dimension_mm_width"]),
        dimension_mm_height=int(confirmed_data["dimension_mm_height"]),
        quantity_units=int(confirmed_data["quantity_units"]),
        deadline_at=str(confirmed_data["deadline_at"]),
        equipment_category=str(confirmed_data["equipment_category"]),
        equipment_duration_days=int(confirmed_data["equipment_duration_days"]),
        maximum_distance_km=25.0,
        maximum_risk=RiskCategory.AMBER,
        extraction_confidence=round(
            sum(item.confidence_score for item in extraction_result.extracted_fields) / max(1, len(extraction_result.extracted_fields)),
            2,
        ),
        input_language=normalize_language_code(extraction_result.detected_language),
        source_type=extraction_result.source_type.value,
        notes="Confirmed from structured AI extraction.",
    )
    return UserConfirmedExtraction(
        request_id=extraction_result.request_id,
        status=ConfirmationStatus.CONFIRMED,
        confirmed_fields=confirmed_field_values,
        warnings=extraction_result.warnings,
        confirmed_demand=demand,
    )


def extract_resource_scan(
    request: AIExtractionRequest,
    provider: AIProvider,
    resource_kind: ResourceKind,
):
    response = provider.extract_resource_scan(request, resource_kind)
    return validate_resource_provider_output(request, response.payload, resource_kind)


def run_confirmed_demand_to_recommendation(
    dataset: DemoDataset,
    request: AIExtractionRequest,
    provider: AIProvider,
    confirmation: ConfirmationInput,
):
    extraction = extract_demand(request, provider)
    confirmed = confirm_demand_extraction(extraction, confirmation)
    if confirmed.confirmed_demand is None:
        raise ValueError("Extraction was not confirmed and cannot proceed to the optimiser.")
    return extraction, confirmed, generate_recommendation(dataset, demand=confirmed.confirmed_demand)


def generate_passport_from_resource_scan(
    request: AIExtractionRequest,
    provider: AIProvider,
    resource_kind: ResourceKind,
    base_passport,
):
    extraction = extract_resource_scan(request, provider, resource_kind)
    if resource_kind == ResourceKind.MATERIAL:
        return extraction, build_material_passport(extraction, base_passport)
    return extraction, build_equipment_passport(extraction, base_passport)
