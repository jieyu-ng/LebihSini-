from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from lebihsini_greenproof.contracts import (
    DemandRequest,
    ExcludedResource,
    MaterialResourcePassport,
    RiskCategory,
    VerificationStatus,
)
from lebihsini_greenproof.explanations import EXPLANATION_TEXT
from lebihsini_greenproof.urgency import add_minutes, format_iso_datetime, minutes_between, parse_iso_datetime


@dataclass(slots=True)
class MaterialCandidateEvaluation:
    resource: MaterialResourcePassport
    eligible: bool
    conditions: list[str] = field(default_factory=list)
    exclusion: ExcludedResource | None = None
    landed_cost_per_unit_myr: float | None = None
    slack_minutes: int | None = None
    transport_carbon_kgco2e: float | None = None
    estimated_arrival_at: str | None = None
    ranking_notes: list[str] = field(default_factory=list)


def _risk_value(risk: RiskCategory) -> int:
    return {
        RiskCategory.GREEN: 1,
        RiskCategory.AMBER: 2,
        RiskCategory.RED: 3,
    }[risk]


def _build_exclusion(
    resource: MaterialResourcePassport,
    reason_code: str,
    reason_text: str,
    evidence_notes: list[str] | None = None,
) -> MaterialCandidateEvaluation:
    return MaterialCandidateEvaluation(
        resource=resource,
        eligible=False,
        exclusion=ExcludedResource(
            resource_id=resource.resource_id,
            site_id=resource.site_id,
            site_name=resource.site_name,
            reason_code=reason_code,
            reason_text=reason_text,
            confidence=resource.confidence,
            evidence_notes=evidence_notes or resource.evidence_notes,
        ),
    )


def evaluate_material_candidate(
    demand: DemandRequest,
    resource: MaterialResourcePassport,
    deadline_at: datetime,
    collection_buffer_minutes: int,
    forbid_material_reuse: bool = False,
) -> MaterialCandidateEvaluation:
    if forbid_material_reuse:
        return _build_exclusion(
            resource,
            "reuse_disabled",
            EXPLANATION_TEXT["normal_procurement_recommended"],
        )
    if resource.category != demand.material_category:
        return _build_exclusion(
            resource,
            "material_category_mismatch",
            "Excluded because the material category does not match the request.",
        )
    if resource.product_code != demand.product_code:
        if resource.site_id == "site-e":
            return _build_exclusion(
                resource,
                "responsible_ai_policy",
                EXPLANATION_TEXT["site_e_uncertainty"],
            )
        return _build_exclusion(
            resource,
            "product_code_mismatch",
            "Excluded because the product specification does not match the request.",
        )
    if (
        resource.dimension_mm_width != demand.dimension_mm_width
        or resource.dimension_mm_height != demand.dimension_mm_height
    ):
        return _build_exclusion(
            resource,
            "dimension_mismatch",
            "Excluded because the material dimensions do not match the request.",
        )
    if resource.quantity_units <= 0:
        return _build_exclusion(
            resource,
            "zero_quantity",
            "Excluded because no usable quantity is available.",
        )
    if resource.distance_to_site_km > demand.maximum_distance_km:
        return _build_exclusion(
            resource,
            "distance_exceeded",
            EXPLANATION_TEXT["distance_exceeded"],
        )
    if resource.risk_category == RiskCategory.RED or _risk_value(resource.risk_category) > _risk_value(demand.maximum_risk):
        return _build_exclusion(
            resource,
            "risk_exceeded",
            EXPLANATION_TEXT["risk_exceeded"] if resource.site_id != "site-e" else EXPLANATION_TEXT["site_e_uncertainty"],
        )
    if not resource.has_required_documentation:
        return _build_exclusion(
            resource,
            "documentation_missing",
            EXPLANATION_TEXT["documentation_missing"] if resource.site_id != "site-e" else EXPLANATION_TEXT["site_e_uncertainty"],
        )
    if resource.verification_status == VerificationStatus.UNVERIFIED:
        return _build_exclusion(
            resource,
            "verification_insufficient",
            EXPLANATION_TEXT["verification_insufficient"] if resource.site_id != "site-e" else EXPLANATION_TEXT["site_e_uncertainty"],
        )

    available_from = parse_iso_datetime(resource.available_from_at)
    collection_start = parse_iso_datetime(resource.collection_window_start_at)
    collection_end = parse_iso_datetime(resource.collection_window_end_at)
    rescue_deadline = parse_iso_datetime(resource.rescue_deadline_at)
    effective_collection_cutoff = min(collection_end, rescue_deadline, deadline_at)
    earliest_collection_start = max(available_from, collection_start)

    if available_from > deadline_at:
        return _build_exclusion(
            resource,
            "available_too_late",
            EXPLANATION_TEXT["available_too_late"],
        )
    if earliest_collection_start > effective_collection_cutoff:
        return _build_exclusion(
            resource,
            "collection_window_missed",
            EXPLANATION_TEXT["collection_window_missed"],
        )

    arrival_at = add_minutes(
        earliest_collection_start,
        collection_buffer_minutes + resource.travel_time_to_site_minutes,
    )
    if arrival_at > deadline_at:
        return _build_exclusion(
            resource,
            "deadline_infeasible",
            EXPLANATION_TEXT["travel_deadline_missed"],
        )

    transport_cost_myr = resource.distance_to_site_km * resource.transport_rate_myr_per_km
    landed_cost_per_unit_myr = resource.transfer_price_myr_per_unit + (
        transport_cost_myr / resource.quantity_units
    )
    transport_carbon_kgco2e = resource.distance_to_site_km * resource.vehicle_factor_kgco2e_per_km
    slack_minutes = minutes_between(arrival_at, deadline_at)
    conditions: list[str] = []
    if resource.risk_category == RiskCategory.AMBER or resource.inspection_required:
        conditions.append(EXPLANATION_TEXT["inspection_required"])

    ranking_notes = [
        f"landed_cost_per_unit_myr={landed_cost_per_unit_myr:.3f}",
        f"slack_minutes={slack_minutes}",
        f"transport_carbon_kgco2e={transport_carbon_kgco2e:.3f}",
        f"estimated_arrival_at={format_iso_datetime(arrival_at)}",
    ]
    return MaterialCandidateEvaluation(
        resource=resource,
        eligible=True,
        conditions=conditions,
        landed_cost_per_unit_myr=landed_cost_per_unit_myr,
        slack_minutes=slack_minutes,
        transport_carbon_kgco2e=transport_carbon_kgco2e,
        estimated_arrival_at=format_iso_datetime(arrival_at),
        ranking_notes=ranking_notes,
    )
