from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from lebihsini_greenproof.contracts import (
    DemandRequest,
    EquipmentResourcePassport,
    ExcludedResource,
    RiskCategory,
    SelectedEquipment,
)
from lebihsini_greenproof.explanations import EXPLANATION_TEXT
from lebihsini_greenproof.urgency import add_days, add_minutes, minutes_between, parse_iso_datetime


MINIMUM_MAINTENANCE_CONFIDENCE = 0.8


@dataclass(slots=True)
class EquipmentEvaluation:
    resource: EquipmentResourcePassport
    eligible: bool
    exclusion: ExcludedResource | None = None
    conditions: list[str] = field(default_factory=list)
    total_cost_myr: float | None = None
    slack_minutes: int | None = None


def _risk_value(risk: RiskCategory) -> int:
    return {
        RiskCategory.GREEN: 1,
        RiskCategory.AMBER: 2,
        RiskCategory.RED: 3,
    }[risk]


def _build_exclusion(
    resource: EquipmentResourcePassport,
    reason_code: str,
    reason_text: str,
) -> EquipmentEvaluation:
    return EquipmentEvaluation(
        resource=resource,
        eligible=False,
        exclusion=ExcludedResource(
            resource_id=resource.resource_id,
            site_id=resource.site_id,
            site_name=resource.site_name,
            reason_code=reason_code,
            reason_text=reason_text,
            confidence=resource.maintenance_confidence,
            evidence_notes=resource.evidence_notes,
        ),
    )


def evaluate_equipment_candidate(
    demand: DemandRequest,
    resource: EquipmentResourcePassport,
    deadline_at: datetime,
    collection_buffer_minutes: int,
    return_buffer_minutes: int,
    force_unavailable_ids: tuple[str, ...] = (),
) -> EquipmentEvaluation:
    if resource.resource_id in force_unavailable_ids:
        return _build_exclusion(
            resource,
            "forced_unavailable",
            "Excluded because this scenario explicitly marked the equipment unavailable.",
        )
    if resource.category != demand.equipment_category:
        return _build_exclusion(
            resource,
            "equipment_category_mismatch",
            "Excluded because the equipment category does not match the request.",
        )
    if resource.risk_category == RiskCategory.RED or _risk_value(resource.risk_category) > _risk_value(demand.maximum_risk):
        return _build_exclusion(
            resource,
            "equipment_risk_exceeded",
            EXPLANATION_TEXT["risk_exceeded"],
        )
    if resource.operator_required:
        return _build_exclusion(
            resource,
            "operator_requirement_unmet",
            EXPLANATION_TEXT["operator_requirement_unmet"],
        )
    if not resource.maintenance_record_present or resource.maintenance_confidence < MINIMUM_MAINTENANCE_CONFIDENCE:
        return _build_exclusion(
            resource,
            "maintenance_insufficient",
            EXPLANATION_TEXT["maintenance_insufficient"],
        )
    if resource.distance_to_site_km > demand.maximum_distance_km:
        return _build_exclusion(
            resource,
            "distance_exceeded",
            EXPLANATION_TEXT["distance_exceeded"],
        )

    availability_start = parse_iso_datetime(resource.availability_start_at)
    availability_end = parse_iso_datetime(resource.availability_end_at)
    collection_start = parse_iso_datetime(resource.collection_window_start_at)
    collection_end = parse_iso_datetime(resource.collection_window_end_at)
    earliest_collection_start = max(availability_start, collection_start)
    required_end = add_days(deadline_at, demand.equipment_duration_days)
    return_deadline = add_minutes(required_end, return_buffer_minutes)

    if availability_start > deadline_at:
        return _build_exclusion(
            resource,
            "available_too_late",
            EXPLANATION_TEXT["available_too_late"],
        )
    if availability_end < return_deadline:
        return _build_exclusion(
            resource,
            "equipment_duration_infeasible",
            EXPLANATION_TEXT["equipment_duration_infeasible"],
        )
    if earliest_collection_start > collection_end or earliest_collection_start > deadline_at:
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

    rental_cost = resource.rental_rate_myr_per_day * demand.equipment_duration_days
    transport_cost = resource.distance_to_site_km * resource.transport_rate_myr_per_km
    slack_minutes = minutes_between(arrival_at, deadline_at)
    conditions: list[str] = []
    if resource.is_commercial_fallback:
        conditions.append(EXPLANATION_TEXT["commercial_equipment_fallback"])

    return EquipmentEvaluation(
        resource=resource,
        eligible=True,
        conditions=conditions,
        total_cost_myr=rental_cost + transport_cost,
        slack_minutes=slack_minutes,
    )


def select_equipment(
    demand: DemandRequest,
    equipment_resources: list[EquipmentResourcePassport],
    fallback_resource: EquipmentResourcePassport,
    deadline_at: datetime,
    collection_buffer_minutes: int,
    return_buffer_minutes: int,
    force_unavailable_ids: tuple[str, ...] = (),
) -> tuple[SelectedEquipment | None, list[ExcludedResource], float]:
    evaluations = [
        evaluate_equipment_candidate(
            demand,
            resource,
            deadline_at,
            collection_buffer_minutes,
            return_buffer_minutes,
            force_unavailable_ids=force_unavailable_ids,
        )
        for resource in [*equipment_resources, fallback_resource]
    ]
    excluded_resources = [item.exclusion for item in evaluations if item.exclusion is not None]
    eligible = [item for item in evaluations if item.eligible]
    eligible.sort(
        key=lambda item: (
            item.resource.is_commercial_fallback,
            round(item.total_cost_myr or 0.0, 6),
            -(item.slack_minutes or 0),
            item.resource.resource_id,
        )
    )
    if not eligible:
        return None, excluded_resources, 0.0
    selected = eligible[0]
    rental_cost = selected.resource.rental_rate_myr_per_day * demand.equipment_duration_days
    return (
        SelectedEquipment(
            resource_id=selected.resource.resource_id,
            site_id=selected.resource.site_id,
            site_name=selected.resource.site_name,
            category=selected.resource.category,
            duration_days=demand.equipment_duration_days,
            rental_cost_myr=rental_cost,
            is_commercial_fallback=selected.resource.is_commercial_fallback,
            conditions=selected.conditions,
        ),
        excluded_resources,
        selected.total_cost_myr or 0.0,
    )
