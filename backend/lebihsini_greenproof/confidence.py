"""Deterministic confidence policy for extraction and passport workflows."""

from __future__ import annotations

from dataclasses import dataclass

from lebihsini_greenproof.contracts import ConfidenceLabel, ExtractedField, MissingFieldWarning


CRITICAL_DEMAND_FIELDS = {
    "material_category",
    "product_code",
    "dimension_mm_width",
    "dimension_mm_height",
    "quantity_units",
    "deadline_at",
    "equipment_category",
}


@dataclass(slots=True)
class ConfidencePolicy:
    high_threshold: float = 0.85
    medium_threshold: float = 0.60


DEFAULT_CONFIDENCE_POLICY = ConfidencePolicy()


def confidence_label(score: float, policy: ConfidencePolicy = DEFAULT_CONFIDENCE_POLICY) -> ConfidenceLabel:
    if not 0.0 <= score <= 1.0:
        raise ValueError("confidence score must be between 0.0 and 1.0.")
    if score >= policy.high_threshold:
        return ConfidenceLabel.HIGH
    if score >= policy.medium_threshold:
        return ConfidenceLabel.MEDIUM
    return ConfidenceLabel.LOW


def confirmation_required(score: float, field_name: str, policy: ConfidencePolicy = DEFAULT_CONFIDENCE_POLICY) -> bool:
    del field_name
    return True


def has_low_confidence_critical_field(
    extracted_fields: list[ExtractedField],
    policy: ConfidencePolicy = DEFAULT_CONFIDENCE_POLICY,
) -> bool:
    return any(
        field.field_name in CRITICAL_DEMAND_FIELDS and field.confidence_score < policy.medium_threshold
        for field in extracted_fields
    )


def identify_missing_critical_fields(normalized_data: dict[str, object]) -> list[MissingFieldWarning]:
    missing: list[MissingFieldWarning] = []
    for field_name in sorted(CRITICAL_DEMAND_FIELDS):
        if normalized_data.get(field_name) in (None, "", [], "UNKNOWN"):
            missing.append(
                MissingFieldWarning(
                    field_name=field_name,
                    message=f"Critical field `{field_name}` is missing and must be confirmed before submission.",
                    critical=True,
                )
            )
    return missing


def may_proceed_to_confirmation(
    extracted_fields: list[ExtractedField],
    missing_fields: list[MissingFieldWarning],
    policy: ConfidencePolicy = DEFAULT_CONFIDENCE_POLICY,
) -> bool:
    del policy
    if any(item.critical for item in missing_fields):
        return False
    return True


def passport_may_enter_automatic_matching(
    confidence_score: float,
    verification_status: str,
    inspection_required: bool,
    policy: ConfidencePolicy = DEFAULT_CONFIDENCE_POLICY,
) -> bool:
    if verification_status == "unverified":
        return False
    if inspection_required:
        return False
    return confidence_score >= policy.medium_threshold
