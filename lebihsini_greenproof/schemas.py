from pydantic import BaseModel
from typing import List, Optional, Any
from .contracts import DemandRequest

class ExtractRequestPayload(BaseModel):
    source_type: str
    content_reference: str
    input_language: Optional[str] = None

class ExtractRequestResponse(BaseModel):
    demand: DemandRequest
    warnings: List[str]

class RecommendationsPayload(BaseModel):
    demand: DemandRequest

class RecalculatePayload(BaseModel):
    scenario_id: str
    revised_deadline_at: str

class DecisionPayload(BaseModel):
    decision_id: str
    recommendation_id: str
    decision_type: str
    decided_by: str
    decided_at: str
    override_notes: str = ""

class DecisionResponse(BaseModel):
    status: str
    decision_id: str

class HealthResponse(BaseModel):
    status: str
