from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any


MALAYSIA_TIMEZONE = "Asia/Kuala_Lumpur"
CALCULATION_VERSION = "foundation-v0.1"


class ResourceKind(StrEnum):
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    SUPPLIER = "supplier"
    PROJECT = "project"


class RiskCategory(StrEnum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"


class VerificationStatus(StrEnum):
    VERIFIED = "verified"
    PARTIAL = "partial"
    UNVERIFIED = "unverified"


class Verdict(StrEnum):
    GREENPROOF_RECOMMENDED = "greenproof_recommended"
    NORMAL_PROCUREMENT_RECOMMENDED = "normal_procurement_recommended"
    PARTIAL_REUSE_RECOMMENDED = "partial_reuse_recommended"


class ApprovalDecisionType(StrEnum):
    APPROVE = "approve"
    MODIFY = "modify"
    REJECT = "reject"
    REQUEST_INSPECTION = "request_inspection"


def _assert_non_negative(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} must be non-negative.")


def _assert_confidence(value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError("confidence must be between 0.0 and 1.0.")


def _assert_iso_datetime(name: str, value: str) -> None:
    try:
        datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO 8601 datetime string.") from exc


@dataclass(slots=True)
class Location:
    site_id: str
    name: str
    cluster: str
    latitude: float
    longitude: float
    timezone: str = MALAYSIA_TIMEZONE


@dataclass(slots=True)
class DemandRequest:
    demand_id: str
    requesting_site_id: str
    material_category: str
    product_code: str
    colour: str
    dimension_mm_width: int
    dimension_mm_height: int
    quantity_units: int
    deadline_at: str
    equipment_category: str
    equipment_duration_days: int
    maximum_distance_km: float
    maximum_risk: RiskCategory
    extraction_confidence: float
    input_language: str
    source_type: str
    notes: str = ""

    def __post_init__(self) -> None:
        _assert_non_negative("quantity_units", self.quantity_units)
        _assert_non_negative("maximum_distance_km", self.maximum_distance_km)
        _assert_confidence(self.extraction_confidence)
        _assert_iso_datetime("deadline_at", self.deadline_at)


@dataclass(slots=True)
class MaterialResourcePassport:
    resource_id: str
    site_id: str
    site_name: str
    category: str
    brand: str
    product_code: str
    dimension_mm_width: int
    dimension_mm_height: int
    colour: str
    quantity_units: int
    transfer_price_myr_per_unit: float
    packaging_status: str
    storage_condition: str
    rescue_deadline_at: str
    available_from_at: str
    collection_window_start_at: str
    collection_window_end_at: str
    distance_to_site_km: float
    travel_time_to_site_minutes: int
    transport_rate_myr_per_km: float
    vehicle_factor_kgco2e_per_km: float
    embodied_carbon_kgco2e_per_unit: float
    confidence: float
    risk_category: RiskCategory
    verification_status: VerificationStatus
    inspection_required: bool
    has_required_documentation: bool
    evidence_notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _assert_non_negative("quantity_units", self.quantity_units)
        _assert_non_negative("transfer_price_myr_per_unit", self.transfer_price_myr_per_unit)
        _assert_non_negative("distance_to_site_km", self.distance_to_site_km)
        _assert_non_negative("travel_time_to_site_minutes", self.travel_time_to_site_minutes)
        _assert_non_negative("transport_rate_myr_per_km", self.transport_rate_myr_per_km)
        _assert_non_negative("vehicle_factor_kgco2e_per_km", self.vehicle_factor_kgco2e_per_km)
        _assert_non_negative("embodied_carbon_kgco2e_per_unit", self.embodied_carbon_kgco2e_per_unit)
        _assert_confidence(self.confidence)
        for name, value in (
            ("rescue_deadline_at", self.rescue_deadline_at),
            ("available_from_at", self.available_from_at),
            ("collection_window_start_at", self.collection_window_start_at),
            ("collection_window_end_at", self.collection_window_end_at),
        ):
            _assert_iso_datetime(name, value)


@dataclass(slots=True)
class EquipmentResourcePassport:
    resource_id: str
    site_id: str
    site_name: str
    category: str
    brand_model: str
    owner: str
    availability_start_at: str
    availability_end_at: str
    collection_window_start_at: str
    collection_window_end_at: str
    rental_rate_myr_per_day: float
    commercial_rental_rate_myr_per_day: float
    distance_to_site_km: float
    travel_time_to_site_minutes: int
    transport_rate_myr_per_km: float
    vehicle_factor_kgco2e_per_km: float
    maintenance_record_present: bool
    maintenance_confidence: float
    operator_required: bool
    risk_category: RiskCategory
    verification_status: VerificationStatus
    evidence_notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        for name, value in (
            ("rental_rate_myr_per_day", self.rental_rate_myr_per_day),
            ("commercial_rental_rate_myr_per_day", self.commercial_rental_rate_myr_per_day),
            ("distance_to_site_km", self.distance_to_site_km),
            ("travel_time_to_site_minutes", self.travel_time_to_site_minutes),
            ("transport_rate_myr_per_km", self.transport_rate_myr_per_km),
            ("vehicle_factor_kgco2e_per_km", self.vehicle_factor_kgco2e_per_km),
        ):
            _assert_non_negative(name, value)
        _assert_confidence(self.maintenance_confidence)
        for name, value in (
            ("availability_start_at", self.availability_start_at),
            ("availability_end_at", self.availability_end_at),
            ("collection_window_start_at", self.collection_window_start_at),
            ("collection_window_end_at", self.collection_window_end_at),
        ):
            _assert_iso_datetime(name, value)


@dataclass(slots=True)
class ResourceCandidate:
    resource_id: str
    resource_kind: ResourceKind
    eligible: bool
    available_quantity_units: int
    confidence: float
    risk_category: RiskCategory
    rank_score: float
    conditions: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _assert_non_negative("available_quantity_units", self.available_quantity_units)
        _assert_confidence(self.confidence)


@dataclass(slots=True)
class SelectedMaterialResource:
    resource_id: str
    site_id: str
    site_name: str
    quantity_units: int
    transfer_price_myr_per_unit: float
    distance_km: float
    inspection_required: bool
    conditions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SelectedEquipment:
    resource_id: str
    site_id: str
    site_name: str
    category: str
    duration_days: int
    rental_cost_myr: float
    conditions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ExcludedResource:
    resource_id: str
    site_id: str
    site_name: str
    reason_code: str
    reason_text: str
    confidence: float

    def __post_init__(self) -> None:
        _assert_confidence(self.confidence)


@dataclass(slots=True)
class CostBreakdown:
    currency: str
    new_material_cost_myr: float
    commercial_equipment_rental_myr: float
    supplier_delivery_cost_myr: float
    disposal_or_storage_cost_myr: float
    reuse_transfer_cost_myr: float
    new_material_shortfall_cost_myr: float
    reuse_transport_cost_myr: float
    equipment_cost_myr: float
    inspection_cost_myr: float
    additional_handling_cost_myr: float
    platform_fee_myr: float
    expected_delay_cost_myr: float
    normal_procurement_baseline_myr: float
    greenproof_total_myr: float
    gross_saving_myr: float
    net_saving_myr: float
    working_capital_protected_myr: float
    assumptions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CarbonBreakdown:
    unit: str
    material_carbon_factor_kgco2e_per_unit: float
    vehicle_factor_kgco2e_per_km: float
    quantity_units: int
    transport_distance_km: float
    number_of_trips: int
    processing_carbon_kgco2e: float
    baseline_carbon_kgco2e: float
    greenproof_carbon_kgco2e: float
    net_carbon_avoided_kgco2e: float
    assumptions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RecommendationOutput:
    recommendation_id: str
    verdict: Verdict
    deadline_met: bool
    selected_material_resources: list[SelectedMaterialResource]
    selected_equipment: SelectedEquipment | None
    excluded_resources: list[ExcludedResource]
    supplier_shortfall_units: int
    quantity_fulfilled_units: int
    cost_breakdown: CostBreakdown
    carbon_breakdown: CarbonBreakdown
    conditions: list[str]
    reasons: list[str]
    assumptions: list[str]
    confidence: float
    calculation_version: str = CALCULATION_VERSION

    def __post_init__(self) -> None:
        _assert_confidence(self.confidence)


@dataclass(slots=True)
class HumanApprovalDecision:
    decision_id: str
    recommendation_id: str
    decision_type: ApprovalDecisionType
    decided_by: str
    decided_at: str
    override_notes: str = ""

    def __post_init__(self) -> None:
        _assert_iso_datetime("decided_at", self.decided_at)


@dataclass(slots=True)
class EvidenceRecord:
    record_id: str
    demand: DemandRequest
    recommendation: RecommendationOutput
    original_request_reference: str
    resources_considered: list[str]
    human_decision: HumanApprovalDecision | None
    overrides: list[str]
    expected_impact_summary: str
    actual_outcome_summary: str | None = None


def to_dict(value: Any) -> Any:
    """Return a JSON-friendly representation of known contract objects.

    Prefer `lebihsini_greenproof.serialization.to_jsonable` for new code.
    This helper remains for backwards compatibility inside the foundation layer.
    """
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value):
        return {key: to_dict(val) for key, val in asdict(value).items()}
    if isinstance(value, list):
        return [to_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: to_dict(val) for key, val in value.items()}
    return value
