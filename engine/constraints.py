from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


RISK_ORDER = {"green": 0, "amber": 1, "red": 2}
DEFAULT_FORBIDDEN_CATEGORIES = {
    "reinforcement_steel",
    "rebar",
    "structural_steel",
    "structural_beam",
    "cement",
    "concrete",
    "fire_rated_component",
    "chemical",
    "hazardous_material",
}


@dataclass(frozen=True)
class ConstraintResult:
    """
    Stores the outcome of a material constraint evaluation,
    including approval status, justification, warnings,
    and any hard constraint violations.
    """
    allowed: bool
    resource_id: str
    site_id: str
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    hard_failures: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.allowed and self.warnings:
            return "allowed_with_conditions"
        if self.allowed:
            return "allowed"
        return "rejected"

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "status": self.status,
            "resource_id": self.resource_id,
            "site_id": self.site_id,
            "reasons": self.reasons,
            "warnings": self.warnings,
            "hard_failures": self.hard_failures,
        }


def norm(value: Any) -> str:
    """Normalize strings for robust comparison."""
    if value is None:
        return ""
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


def as_float(value: Any, default: float = 0.0) -> float:
    """Safely converts a value to a float."""
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int = 0) -> int:
    """Safely converts a value to an integer."""
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def as_bool(value: Any, default: bool = False) -> bool:
    """Safely converts a value to a Boolean."""
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"true", "yes", "y", "1", "readable", "verified"}:
        return True
    if text in {"false", "no", "n", "0", "unreadable", "missing"}:
        return False
    return default


def get_dimensions_mm(item: dict[str, Any]) -> tuple[int, ...]:
    """
    Extracts and normalizes material dimensions into
    a tuple of positive integer measurements in millimetres.
    """
    raw = item.get("dimensions_mm") or item.get("dimensions") or item.get("size_mm") or item.get("size")
    if isinstance(raw, dict):
        values = [raw.get("width"), raw.get("height"), raw.get("length")]
        return tuple(as_int(v) for v in values if v is not None and as_int(v) > 0)
    if isinstance(raw, (list, tuple)):
        return tuple(as_int(v) for v in raw if as_int(v) > 0)
    if isinstance(raw, str):
        cleaned = raw.lower().replace("×", "x").replace("*", "x").replace("mm", "")
        parts = [p.strip() for p in cleaned.split("x")]
        return tuple(as_int(p) for p in parts if as_int(p) > 0)
    return tuple()


def risk_level(value: Any) -> str:
    """
    Normalizes and validates a risk level, returning a
    supported risk category or the default level.
    """
    risk = norm(value) or "amber"
    return risk if risk in RISK_ORDER else "amber"


def risk_allowed(resource_risk: str, tolerance: str) -> bool:
    """
    Determines whether a resource's risk level is within
    the acceptable tolerance threshold.
    """
    return RISK_ORDER[risk_level(resource_risk)] <= RISK_ORDER[risk_level(tolerance)]


def material_matches_demand(resource: dict[str, Any], demand: dict[str, Any]) -> bool:
    """
    Checks whether a material resource generally matches
    the requested material category and dimensions.
    """
    return (
        norm(resource.get("category")) == norm(demand.get("material_category") or demand.get("category"))
        and get_dimensions_mm(resource) == get_dimensions_mm(demand)
    )


def deadline_hours_from_demand(demand: dict[str, Any]) -> float:
    """
    Retrieves and standardizes the deadline requirement
    from a demand record in hours.
    """
    return as_float(demand.get("deadline_hours", demand.get("required_within_hours", 24)), 24.0)


def can_meet_deadline(resource: dict[str, Any], demand: dict[str, Any]) -> tuple[bool, str]:
    """
    Deadline rule:
    Resource must be available early enough to collect, travel, and reach the receiving site before the demand deadline.
    If pickup_deadline_hours is provided, collection must also happen before that rescue deadline.
    """
    deadline_h = deadline_hours_from_demand(demand)
    available_from_h = as_float(resource.get("available_from_hours", resource.get("ready_in_hours", 0)), 0.0)
    travel_h = as_float(resource.get("travel_minutes", 0), 0.0) / 60.0
    pickup_deadline_h = resource.get("pickup_deadline_hours", resource.get("collection_deadline_hours"))

    latest_collection_h = max(0.0, deadline_h - travel_h)
    if pickup_deadline_h is not None:
        latest_collection_h = min(latest_collection_h, as_float(pickup_deadline_h, latest_collection_h))

    if available_from_h > latest_collection_h:
        return (
            False,
            f"Cannot meet deadline: available at {available_from_h:.1f}h, latest safe collection is {latest_collection_h:.1f}h.",
        )
    return True, f"Can meet deadline: available at {available_from_h:.1f}h, travel time {travel_h:.1f}h."


def check_material_constraints(
    resource: dict[str, Any],
    demand: dict[str, Any],
    *,
    forbidden_categories: set[str] | None = None,
    min_confidence: float = 0.70,
) -> ConstraintResult:
    """
    Apply hard construction rules before cost/carbon optimisation.
    Returns an explainable accept/reject result for one surplus material resource.
    """
    forbidden_categories = forbidden_categories or DEFAULT_FORBIDDEN_CATEGORIES
    rid = str(resource.get("resource_id") or resource.get("id") or "unknown_resource")
    site = str(resource.get("site_id") or resource.get("site") or resource.get("site_name") or "unknown_site")

    reasons: list[str] = []
    warnings: list[str] = []
    failures: list[str] = []

    demand_category = norm(demand.get("material_category") or demand.get("category"))
    resource_category = norm(resource.get("category") or resource.get("material_category"))

    if not demand_category:
        failures.append("Demand material category is missing.")
    elif resource_category != demand_category:
        failures.append(f"Category mismatch: required {demand_category}, found {resource_category or 'missing'}.")
    elif resource_category in forbidden_categories:
        failures.append(f"Material category {resource_category} is excluded from automatic reuse.")
    else:
        reasons.append("Material category matches.")

    required_dims = get_dimensions_mm(demand)
    resource_dims = get_dimensions_mm(resource)
    substitution_allowed = as_bool(demand.get("substitution_allowed"), False)
    if required_dims and resource_dims:
        if resource_dims != required_dims and not substitution_allowed:
            failures.append(f"Dimension mismatch: required {required_dims}, found {resource_dims}.")
        elif resource_dims != required_dims and substitution_allowed:
            warnings.append(f"Dimension differs from request: required {required_dims}, found {resource_dims}.")
        else:
            reasons.append("Dimensions match.")
    elif required_dims:
        failures.append("Resource dimensions are missing.")

    required_code = norm(demand.get("product_code") or demand.get("brand_code"))
    resource_code = norm(resource.get("product_code") or resource.get("brand_code"))
    if required_code:
        if not resource_code:
            failures.append("Required product code is missing from resource evidence.")
        elif resource_code != required_code and not substitution_allowed:
            failures.append(f"Product code mismatch: required {required_code}, found {resource_code}.")
        elif resource_code != required_code and substitution_allowed:
            warnings.append(f"Product code differs: required {required_code}, found {resource_code}.")
        else:
            reasons.append("Product code matches.")

    required_colour = norm(demand.get("colour") or demand.get("color"))
    resource_colour = norm(resource.get("colour") or resource.get("color"))
    if required_colour:
        if not resource_colour:
            warnings.append("Colour evidence is missing; buyer confirmation required.")
        elif resource_colour != required_colour:
            warnings.append(f"Colour differs: required {required_colour}, found {resource_colour}.")
        else:
            reasons.append("Colour matches.")

    quantity = as_int(resource.get("quantity", resource.get("available_quantity", 0)), 0)
    if quantity <= 0:
        failures.append("Available quantity is zero.")
    else:
        reasons.append(f"{quantity} units available.")

    max_distance_km = as_float(demand.get("max_distance_km", 999999), 999999.0)
    distance_km = as_float(resource.get("distance_km", 0), 0.0)
    if distance_km > max_distance_km:
        failures.append(f"Distance {distance_km:.1f} km exceeds maximum {max_distance_km:.1f} km.")
    else:
        reasons.append(f"Distance {distance_km:.1f} km is within limit.")

    ok_deadline, deadline_reason = can_meet_deadline(resource, demand)
    if ok_deadline:
        reasons.append(deadline_reason)
    else:
        failures.append(deadline_reason)

    tolerance = risk_level(demand.get("risk_tolerance", "amber"))
    r_risk = risk_level(resource.get("risk", resource.get("risk_category", "amber")))
    if not risk_allowed(r_risk, tolerance):
        failures.append(f"Risk {r_risk} exceeds tolerance {tolerance}.")
    elif r_risk == "amber":
        warnings.append("Amber risk: buyer inspection or confirmation required.")
    else:
        reasons.append("Risk category is green.")

    if r_risk == "red":
        failures.append("Red risk resources are excluded from automatic recommendation.")

    if not as_bool(resource.get("label_readable", resource.get("product_label_readable", True)), True):
        failures.append("Product label is unreadable; manual verification required.")

    confidence = as_float(resource.get("confidence", resource.get("ai_confidence", 1.0)), 1.0)
    if confidence < min_confidence:
        failures.append(f"AI confidence {confidence:.2f} is below minimum {min_confidence:.2f}.")
    elif confidence < 0.85:
        warnings.append(f"Medium AI confidence {confidence:.2f}; user confirmation required.")
    else:
        reasons.append(f"AI confidence {confidence:.2f} is acceptable.")

    packaging = norm(resource.get("packaging_status") or resource.get("packaging") or resource.get("condition"))
    if packaging in {"weather_exposed", "outdoor_storage", "damaged", "moisture_exposed"}:
        if r_risk == "green":
            warnings.append(f"Packaging/storage condition is {packaging}; inspection recommended.")
        else:
            failures.append(f"Packaging/storage condition is {packaging}; not suitable for automatic recommendation.")

    allowed = not failures
    return ConstraintResult(
        allowed=allowed,
        resource_id=rid,
        site_id=site,
        reasons=reasons,
        warnings=warnings,
        hard_failures=failures,
    )


def filter_material_resources(
    resources: list[dict[str, Any]],
    demand: dict[str, Any],
    *,
    min_confidence: float = 0.70,
) -> tuple[list[tuple[dict[str, Any], ConstraintResult]], list[dict[str, Any]]]:
    """Return allowed resources plus rejected resources with reasons."""
    allowed: list[tuple[dict[str, Any], ConstraintResult]] = []
    rejected: list[dict[str, Any]] = []

    for resource in resources:
        result = check_material_constraints(resource, demand, min_confidence=min_confidence)
        if result.allowed:
            allowed.append((resource, result))
        else:
            rejected.append({"resource": resource, "constraint_result": result.to_dict()})

    return allowed, rejected
