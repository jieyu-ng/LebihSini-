from __future__ import annotations

from fastapi import APIRouter, Depends

from lebihsini_greenproof.api.dependencies import get_evidence_service
from lebihsini_greenproof.api.models import DecisionBody
from lebihsini_greenproof.services.evidence_service import EvidenceService


router = APIRouter(tags=["decisions"])


@router.post("/recommendations/{recommendation_id}/decision")
def create_decision(
    recommendation_id: str,
    body: DecisionBody,
    service: EvidenceService = Depends(get_evidence_service),
) -> dict:
    decision, evidence = service.record_decision(
        recommendation_id,
        decision_type=body.decision_type,
        actor_reference=body.actor_reference,
        decided_at=body.decided_at,
        override_notes=body.override_notes,
        modified_plan_details=body.modified_plan_details,
    )
    return {"decision": decision, "evidence_record": evidence}


@router.get("/evidence-records/{record_id}")
def get_evidence_record(
    record_id: str,
    service: EvidenceService = Depends(get_evidence_service),
) -> dict:
    return service.get_evidence_record(record_id)
