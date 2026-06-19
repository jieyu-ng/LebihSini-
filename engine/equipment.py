from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:  # Works when files are imported as a package or copied into the same folder.
    from .constraints import as_bool, as_float, norm
except ImportError:  # pragma: no cover
    from constraints import as_bool, as_float, norm


@dataclass(frozen=True)
class EquipmentDecision:
    """
    Stores the outcome of equipment selection.

    Keeps track of the chosen equipment, its source,
    reasons for the decision, excluded alternatives,
    and any fallback option.
    """
    selected: dict[str, Any] | None
    source_type: str
    reasons: list[str] = field(default_factory=list)
    excluded: list[dict[str, Any]] = field(default_factory=list)
    fallback: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected": self.selected,
            "source_type": self.source_type,
            "reasons": self.reasons,
            "excluded": self.excluded,
            "fallback": self.fallback,
        }


def equipment_request_from_demand(demand: dict[str, Any]) -> dict[str, Any] | None:
    """
    Extracts or constructs an equipment request from a demand record.

    Returns a standardized equipment request containing the required
    equipment type, duration, and start time, or None if no equipment
    requirement exists.
    """
    request = demand.get("equipment") or demand.get("equipment_request")
    if isinstance(request, dict) and request.get("type"):
        return request
    equipment_type = demand.get("equipment_type")
    if equipment_type:
        return {
            "type": equipment_type,
            "duration_days": demand.get("equipment_duration_days", demand.get("duration_days", 1)),
            "start_in_hours": demand.get("equipment_start_in_hours", demand.get("deadline_hours", 24)),
        }
    return None


def _equipment_available_for_period(equipment: dict[str, Any], request: dict[str, Any]) -> tuple[bool, str]:
    """
    Checks whether equipment can satisfy the requested usage period.

    Verifies that the equipment can arrive before the job starts and
    remains available for the entire requested duration. Returns the
    evaluation result and an explanatory message.
    """
    start_h = as_float(request.get("start_in_hours", 0), 0.0)
    duration_days = as_float(request.get("duration_days", 1), 1.0)
    end_h = start_h + max(0.0, duration_days) * 24.0

    available_from_h = as_float(equipment.get("available_from_hours", 0), 0.0)
    available_until_h = as_float(equipment.get("available_until_hours", 999999), 999999.0)
    travel_h = as_float(equipment.get("travel_minutes", 0), 0.0) / 60.0

    # Equipment has to reach the receiving site before the job starts.
    latest_dispatch_h = start_h - travel_h
    if available_from_h > latest_dispatch_h:
        return False, f"Equipment cannot arrive before start: ready at {available_from_h:.1f}h, latest dispatch {latest_dispatch_h:.1f}h."
    if available_until_h < end_h:
        return False, f"Equipment availability ends at {available_until_h:.1f}h, but required until {end_h:.1f}h."
    return True, f"Equipment available for {duration_days:g} day(s) and can arrive before start."


def check_equipment_candidate(
    equipment: dict[str, Any],
    request: dict[str, Any],
    demand: dict[str, Any],
) -> tuple[bool, list[str], list[str]]:
    """
    Evaluates whether an equipment candidate satisfies all hard
    selection constraints, including type, distance, availability,
    maintenance status, condition, and operator requirements.

    Returns the evaluation result together with success reasons
    and failure explanations.
    """
    reasons: list[str] = []
    failures: list[str] = []

    required_type = norm(request.get("type"))
    candidate_type = norm(equipment.get("type") or equipment.get("category"))
    if not required_type:
        failures.append("Equipment request type is missing.")
    elif candidate_type != required_type:
        failures.append(f"Equipment type mismatch: required {required_type}, found {candidate_type or 'missing'}.")
    else:
        reasons.append("Equipment type matches.")

    max_distance_km = as_float(demand.get("max_distance_km", 999999), 999999.0)
    distance_km = as_float(equipment.get("distance_km", 0), 0.0)
    if distance_km > max_distance_km:
        failures.append(f"Equipment distance {distance_km:.1f} km exceeds maximum {max_distance_km:.1f} km.")
    else:
        reasons.append(f"Equipment distance {distance_km:.1f} km is within limit.")

    ok_period, period_reason = _equipment_available_for_period(equipment, request)
    if ok_period:
        reasons.append(period_reason)
    else:
        failures.append(period_reason)

    maintenance_status = norm(equipment.get("maintenance_status") or equipment.get("maintenance"))
    maintenance_present = as_bool(equipment.get("maintenance_record_present", equipment.get("maintenance_evidence", True)), True)
    if maintenance_status in {"failed", "overdue", "unknown_bad"} or not maintenance_present:
        failures.append("Maintenance evidence is missing, failed, or overdue.")
    else:
        reasons.append("Maintenance evidence is acceptable.")

    if norm(equipment.get("condition")) in {"damaged", "unsafe", "unknown_bad"}:
        failures.append("Equipment condition is not acceptable.")

    operator_required = as_bool(equipment.get("operator_required"), False)
    operator_available = as_bool(equipment.get("operator_available", True), True)
    if operator_required and not operator_available:
        failures.append("Equipment requires an operator, but no operator is available.")
    elif operator_required:
        reasons.append("Required operator is available.")

    return not failures, reasons, failures


def rank_equipment(equipment: dict[str, Any]) -> tuple[float, float, float]:
    """
    Generates a ranking key for equipment candidates.

    Prioritizes lower rental cost, shorter travel distance,
    and higher confidence when comparing valid equipment.
    """
    rate = as_float(equipment.get("rate_per_day", equipment.get("price_per_day", 0)), 0.0)
    distance = as_float(equipment.get("distance_km", 0), 0.0)
    confidence_penalty = 1.0 - as_float(equipment.get("confidence", 1.0), 1.0)
    return (rate, distance, confidence_penalty)


def select_equipment(
    equipment_resources: list[dict[str, Any]],
    demand: dict[str, Any],
    *,
    fallback: dict[str, Any] | None = None,
) -> EquipmentDecision:
    """
    Selects the most suitable equipment for a demand.

    Validates all available equipment against hard constraints,
    ranks eligible candidates, and chooses the best option.
    If no valid equipment exists, a commercial fallback is returned.
    """
    request = equipment_request_from_demand(demand)
    if request is None:
        return EquipmentDecision(
            selected=None,
            source_type="not_required",
            reasons=["No equipment requested."],
            excluded=[],
            fallback=None,
        )

    valid: list[tuple[dict[str, Any], list[str]]] = []
    excluded: list[dict[str, Any]] = []

    for equipment in equipment_resources:
        ok, reasons, failures = check_equipment_candidate(equipment, request, demand)
        item = {
            "equipment": equipment,
            "reasons": reasons,
            "hard_failures": failures,
        }
        if ok:
            valid.append((equipment, reasons))
        else:
            excluded.append(item)

    if valid:
        selected, reasons = sorted(valid, key=lambda pair: rank_equipment(pair[0]))[0]
        return EquipmentDecision(
            selected=selected,
            source_type="idle_equipment",
            reasons=reasons,
            excluded=excluded,
            fallback=fallback,
        )

    commercial = fallback or {
        "equipment_id": "commercial-rental-fallback",
        "type": request.get("type"),
        "source_name": "Commercial rental fallback",
        "rate_per_day": as_float(request.get("commercial_rate_per_day", 120), 120.0),
        "distance_km": 0,
        "maintenance_status": "commercial_provider_responsibility",
    }
    return EquipmentDecision(
        selected=commercial,
        source_type="commercial_fallback",
        reasons=["No suitable idle equipment passed the hard constraints; commercial fallback selected."],
        excluded=excluded,
        fallback=commercial,
    )
