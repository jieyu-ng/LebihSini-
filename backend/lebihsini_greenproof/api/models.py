from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from lebihsini_greenproof.contracts import (
    ApprovalDecisionType,
    ConfirmationAction,
    InputSourceType,
    RiskCategory,
)


class ExtractRequestBody(BaseModel):
    request_id: str
    source_type: InputSourceType
    content: str
    content_reference: str
    input_language: str | None = None
    reference_datetime: str | None = None
    timezone: str = "Asia/Kuala_Lumpur"


class ConfirmExtractionBody(BaseModel):
    action: ConfirmationAction
    confirmed_values: dict[str, Any] = Field(default_factory=dict)
    confirmed_at: str


class MaterialPassportBody(ExtractRequestBody):
    resource_id: str
    human_confirmed_quantity_units: int | None = None


class EquipmentPassportBody(ExtractRequestBody):
    resource_id: str


class DemandRequestBody(BaseModel):
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


class RecommendationCreateBody(BaseModel):
    confirmed_demand_id: str | None = None
    confirmed_demand: DemandRequestBody | None = None


class RecommendationRecalculateBody(BaseModel):
    revised_deadline_at: str
    force_equipment_unavailable_ids: list[str] = Field(default_factory=list)
    forbid_material_reuse: bool = False
    allow_reuse_when_net_carbon_negative: bool = False


class DecisionBody(BaseModel):
    decision_type: ApprovalDecisionType
    actor_reference: str
    decided_at: str
    override_notes: str = ""
    modified_plan_details: dict[str, Any] = Field(default_factory=dict)
