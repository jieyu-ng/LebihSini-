from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta

from lebihsini_greenproof.contracts import DemandRequest


@dataclass(slots=True)
class RecommendationScenario:
    scenario_id: str
    revised_deadline_at: str | None = None
    equipment_required: bool = True
    allow_reuse_when_net_carbon_negative: bool = False
    force_equipment_unavailable_ids: tuple[str, ...] = ()
    forbid_material_reuse: bool = False


def parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def format_iso_datetime(value: datetime) -> str:
    return value.isoformat()


def resolve_deadline_at(demand: DemandRequest, scenario: RecommendationScenario | None = None) -> datetime:
    if scenario and scenario.revised_deadline_at:
        return parse_iso_datetime(scenario.revised_deadline_at)
    return parse_iso_datetime(demand.deadline_at)


def revise_demand_deadline(demand: DemandRequest, deadline_at: str) -> DemandRequest:
    return replace(demand, deadline_at=deadline_at)


def add_minutes(value: datetime, minutes: int) -> datetime:
    return value + timedelta(minutes=minutes)


def add_days(value: datetime, days: int) -> datetime:
    return value + timedelta(days=days)


def minutes_between(start: datetime, end: datetime) -> int:
    return int((end - start).total_seconds() // 60)
