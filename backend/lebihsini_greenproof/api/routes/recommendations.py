from __future__ import annotations

from fastapi import APIRouter, Depends

from lebihsini_greenproof.api.dependencies import get_recommendation_service
from lebihsini_greenproof.api.models import DemandRequestBody, RecommendationCreateBody, RecommendationRecalculateBody
from lebihsini_greenproof.contracts import DemandRequest
from lebihsini_greenproof.serialization import to_jsonable
from lebihsini_greenproof.services.recommendation_service import RecommendationService
from lebihsini_greenproof.urgency import RecommendationScenario


router = APIRouter(tags=["recommendations"])


@router.post("/recommendations")
def create_recommendation(
    body: RecommendationCreateBody,
    service: RecommendationService = Depends(get_recommendation_service),
) -> dict:
    demand = DemandRequest(**body.confirmed_demand.model_dump()) if body.confirmed_demand is not None else None
    recommendation = service.create_recommendation(
        confirmed_demand_id=body.confirmed_demand_id,
        demand=demand,
    )
    return to_jsonable(recommendation)


@router.post("/recommendations/{recommendation_id}/recalculate")
def recalculate_recommendation(
    recommendation_id: str,
    body: RecommendationRecalculateBody,
    service: RecommendationService = Depends(get_recommendation_service),
) -> dict:
    recommendation = service.recalculate_recommendation(
        recommendation_id,
        RecommendationScenario(
            scenario_id=f"recalc-{recommendation_id}",
            revised_deadline_at=body.revised_deadline_at,
            force_equipment_unavailable_ids=tuple(body.force_equipment_unavailable_ids),
            forbid_material_reuse=body.forbid_material_reuse,
            allow_reuse_when_net_carbon_negative=body.allow_reuse_when_net_carbon_negative,
        ),
    )
    return to_jsonable(recommendation)
