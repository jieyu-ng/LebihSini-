from __future__ import annotations

from datetime import timedelta

from lebihsini_greenproof.confidence import (
    confidence_label,
    confirmation_required,
    identify_missing_critical_fields,
    may_proceed_to_confirmation,
)
from lebihsini_greenproof.contracts import (
    AIExtractionRequest,
    AIModelMetadata,
    ConfidenceLabel,
    ExtractedField,
    InputSourceType,
    MissingFieldWarning,
    ProcessingWarning,
    ProviderStatus,
    RawEvidenceReference,
    ResourceKind,
    ResourceScanExtractionResult,
    StructuredDemandExtractionResult,
)
from lebihsini_greenproof.input_processing import normalize_language_code
from lebihsini_greenproof.urgency import format_iso_datetime, parse_iso_datetime


BAHASA_CATEGORY_SYNONYMS = {
    "tile": "porcelain_tile",
    "porcelain tile": "porcelain_tile",
    "mesin pemotong": "tile_cutter",
}


def _parse_confidence(value: object) -> float:
    if isinstance(value, str):
        normalized = value.strip().replace("%", "")
        parsed = float(normalized)
        if parsed > 1.0:
            parsed = parsed / 100.0
        return parsed
    if isinstance(value, int | float):
        parsed = float(value)
        if parsed > 1.0:
            parsed = parsed / 100.0
        return parsed
    raise ValueError("Unsupported confidence value.")


def _parse_dimensions(value: object) -> tuple[int | None, int | None]:
    if value is None:
        return None, None
    if isinstance(value, str):
        cleaned = (
            value.lower()
            .replace("mm", "")
            .replace("kali", "x")
            .replace("×", "x")
            .replace(" ", "")
        )
        if "x" in cleaned:
            left, right = cleaned.split("x", 1)
            return int(left), int(right)
    raise ValueError("Unsupported dimension format.")


def _parse_int(value: object) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        return int(value.strip())
    raise ValueError("Unsupported integer value.")


def _resolve_relative_deadline(
    relative_value: object,
    request: AIExtractionRequest,
) -> str | None:
    if relative_value is None:
        return None
    if request.reference_datetime is None:
        raise ValueError("Relative deadline requires a reference datetime.")
    reference = parse_iso_datetime(request.reference_datetime)
    text = str(relative_value).strip().lower()
    if text == "tomorrow":
        return format_iso_datetime((reference + timedelta(days=1)).replace(hour=11, minute=0, second=0, microsecond=0))
    if text == "tomorrow 11:00":
        return format_iso_datetime((reference + timedelta(days=1)).replace(hour=11, minute=0, second=0, microsecond=0))
    if text == "esok":
        return format_iso_datetime((reference + timedelta(days=1)).replace(hour=11, minute=0, second=0, microsecond=0))
    return str(relative_value)


def _evidence_reference(request: AIExtractionRequest, field_name: str) -> RawEvidenceReference:
    return RawEvidenceReference(
        reference_id=f"{request.request_id}:{field_name}",
        source_type=request.source_type,
        content_reference=request.content_reference,
        note=f"Derived from {request.source_type.value}.",
    )


def validate_demand_provider_output(
    request: AIExtractionRequest,
    provider_payload: dict,
) -> StructuredDemandExtractionResult:
    if "fields" not in provider_payload or not isinstance(provider_payload["fields"], dict):
        raise ValueError("Provider payload is missing `fields`.")
    fields_payload = provider_payload["fields"]
    warnings: list[ProcessingWarning] = []
    normalized_data: dict[str, object] = {
        "material_category": None,
        "product_code": None,
        "colour": None,
        "dimension_mm_width": None,
        "dimension_mm_height": None,
        "quantity_units": None,
        "deadline_at": None,
        "equipment_category": None,
        "equipment_duration_days": None,
    }
    extracted_fields: list[ExtractedField] = []

    for field_name, spec in fields_payload.items():
        raw_value = spec.get("value")
        score = _parse_confidence(spec.get("confidence", 0.0))
        label = confidence_label(score)
        warning_text: str | None = None
        normalized_value = raw_value
        if field_name == "dimensions":
            width, height = _parse_dimensions(raw_value)
            normalized_data["dimension_mm_width"] = width
            normalized_data["dimension_mm_height"] = height
            extracted_fields.extend(
                [
                    ExtractedField(
                        field_name="dimension_mm_width",
                        extracted_value=width,
                        confidence_score=score,
                        confidence_label=label,
                        evidence_reference=_evidence_reference(request, "dimension_mm_width"),
                        confirmation_required=confirmation_required(score, "dimension_mm_width"),
                    ),
                    ExtractedField(
                        field_name="dimension_mm_height",
                        extracted_value=height,
                        confidence_score=score,
                        confidence_label=label,
                        evidence_reference=_evidence_reference(request, "dimension_mm_height"),
                        confirmation_required=confirmation_required(score, "dimension_mm_height"),
                    ),
                ]
            )
            continue
        if field_name == "quantity_units":
            normalized_value = _parse_int(raw_value)
        elif field_name == "equipment_duration_days":
            normalized_value = _parse_int(raw_value)
        elif field_name == "deadline_relative":
            normalized_value = _resolve_relative_deadline(raw_value, request)
            field_name = "deadline_at"
        elif field_name == "material_category":
            normalized_value = BAHASA_CATEGORY_SYNONYMS.get(str(raw_value).lower(), raw_value)
        elif field_name == "equipment_category":
            normalized_value = BAHASA_CATEGORY_SYNONYMS.get(str(raw_value).lower(), raw_value)
        elif field_name == "product_code" and raw_value in ("UNKNOWN", "", None):
            normalized_value = None
            warning_text = "Product code could not be verified from the visible evidence."

        normalized_data[field_name] = normalized_value
        extracted_fields.append(
            ExtractedField(
                field_name=field_name,
                extracted_value=normalized_value,
                confidence_score=score,
                confidence_label=label,
                evidence_reference=_evidence_reference(request, field_name),
                confirmation_required=confirmation_required(score, field_name),
                warning=warning_text,
            )
        )

    missing_fields = identify_missing_critical_fields(normalized_data)
    if any(field.confidence_label == ConfidenceLabel.MEDIUM for field in extracted_fields):
        warnings.append(
            ProcessingWarning(
                code="LOW_CONFIDENCE_CONFIRMATION_REQUIRED",
                message="One or more extracted fields require careful confirmation before submission.",
            )
        )
    if any(field.confidence_label == ConfidenceLabel.LOW for field in extracted_fields):
        warnings.append(
            ProcessingWarning(
                code="LOW_CONFIDENCE_CONFIRMATION_REQUIRED",
                message="Low-confidence critical fields must be confirmed or corrected before submission.",
            )
        )
    warnings.extend(
        ProcessingWarning(
            code="MISSING_CRITICAL_FIELD",
            message=item.message,
            field_name=item.field_name,
        )
        for item in missing_fields
    )
    return StructuredDemandExtractionResult(
        request_id=request.request_id,
        source_type=request.source_type,
        detected_language=normalize_language_code(provider_payload.get("provider_language") or request.input_language),
        extracted_fields=extracted_fields,
        missing_fields=missing_fields,
        warnings=warnings,
        model_metadata=AIModelMetadata(
            provider_name=provider_payload.get("provider_name", "unknown"),
            model_name=provider_payload.get("model_name", "unknown"),
            model_version=provider_payload.get("model_version", "unknown"),
            status=ProviderStatus(provider_payload.get("status", ProviderStatus.SUCCESS.value)),
            request_id=provider_payload.get("request_id", request.request_id),
            operation_type=provider_payload.get("operation_type"),
        ),
        can_proceed_to_confirmation=may_proceed_to_confirmation(extracted_fields, missing_fields),
        requires_manual_review=bool(missing_fields),
        normalized_demand=normalized_data,
    )


def validate_resource_provider_output(
    request: AIExtractionRequest,
    provider_payload: dict,
    resource_kind: ResourceKind,
) -> ResourceScanExtractionResult:
    if "fields" not in provider_payload or not isinstance(provider_payload["fields"], dict):
        raise ValueError("Provider payload is missing `fields`.")
    extracted_fields: list[ExtractedField] = []
    warnings: list[ProcessingWarning] = []
    normalized_data: dict[str, object] = {}
    for field_name, spec in provider_payload["fields"].items():
        raw_value = spec.get("value")
        score = _parse_confidence(spec.get("confidence", 0.0))
        label = confidence_label(score)
        normalized_value = raw_value
        if field_name == "dimensions":
            width, height = _parse_dimensions(raw_value)
            normalized_data["dimension_mm_width"] = width
            normalized_data["dimension_mm_height"] = height
            extracted_fields.extend(
                [
                    ExtractedField(
                        field_name="dimension_mm_width",
                        extracted_value=width,
                        confidence_score=score,
                        confidence_label=label,
                        evidence_reference=_evidence_reference(request, "dimension_mm_width"),
                        confirmation_required=True,
                    ),
                    ExtractedField(
                        field_name="dimension_mm_height",
                        extracted_value=height,
                        confidence_score=score,
                        confidence_label=label,
                        evidence_reference=_evidence_reference(request, "dimension_mm_height"),
                        confirmation_required=True,
                    ),
                ]
            )
            continue
        if field_name in {"quantity_estimate_units"}:
            normalized_value = _parse_int(raw_value)
        normalized_data[field_name] = normalized_value
        extracted_fields.append(
            ExtractedField(
                field_name=field_name,
                extracted_value=normalized_value,
                confidence_score=score,
                confidence_label=label,
                evidence_reference=_evidence_reference(request, field_name),
                confirmation_required=True,
            )
        )

    if normalized_data.get("product_code") in (None, "") and resource_kind == ResourceKind.MATERIAL:
        warnings.append(
            ProcessingWarning(
                code="MANUAL_INSPECTION_REQUIRED",
                message="Product code could not be verified from the resource scan.",
                field_name="product_code",
            )
        )
    return ResourceScanExtractionResult(
        request_id=request.request_id,
        source_type=request.source_type,
        resource_kind=resource_kind,
        detected_language=normalize_language_code(provider_payload.get("provider_language") or request.input_language),
        extracted_fields=extracted_fields,
        missing_fields=[],
        warnings=warnings,
        model_metadata=AIModelMetadata(
            provider_name=provider_payload.get("provider_name", "unknown"),
            model_name=provider_payload.get("model_name", "unknown"),
            model_version=provider_payload.get("model_version", "unknown"),
            status=ProviderStatus(provider_payload.get("status", ProviderStatus.SUCCESS.value)),
            request_id=provider_payload.get("request_id", request.request_id),
            operation_type=provider_payload.get("operation_type"),
        ),
        can_generate_passport=True,
        requires_manual_review=bool(warnings),
        normalized_resource_data=normalized_data,
    )
