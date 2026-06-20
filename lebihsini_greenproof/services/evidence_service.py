from __future__ import annotations

from datetime import datetime

from lebihsini_greenproof.contracts import (
    ApprovalDecisionType,
    CALCULATION_VERSION,
    HumanApprovalDecision,
    to_dict,
)
from lebihsini_greenproof.demo_data import DemoDataset
from lebihsini_greenproof.repositories.in_memory import InMemoryRepository
from lebihsini_greenproof.services.extraction_service import ServiceError


from lebihsini_greenproof.repositories import WorkflowRepository, EvidenceRecordRepository

class EvidenceService:
    def __init__(self, repository: WorkflowRepository, dataset: DemoDataset, evidence_repository: EvidenceRecordRepository | None = None) -> None:
        self.repository = repository
        self.dataset = dataset
        self.evidence_repository = evidence_repository

    def record_decision(
        self,
        recommendation_id: str,
        *,
        decision_type: ApprovalDecisionType,
        actor_reference: str,
        decided_at: str,
        override_notes: str = "",
        modified_plan_details: dict | None = None,
    ) -> tuple[dict, dict]:
        stored = self.repository.recommendations.get(recommendation_id)
        if stored is None:
            raise ServiceError("RECOMMENDATION_NOT_FOUND", "Recommendation was not found.", status_code=404)

        decision_id = self.repository.next_decision_id()
        decision = HumanApprovalDecision(
            decision_id=decision_id,
            recommendation_id=recommendation_id,
            decision_type=decision_type,
            decided_by=actor_reference,
            decided_at=decided_at,
            override_notes=override_notes,
        )
        decision_payload = {
            **to_dict(decision),
            "actor_reference": actor_reference,
            "modified_plan_details": modified_plan_details or {},
        }
        self.repository.decisions[decision_id] = decision_payload

        extraction_snapshot = self._find_extraction_for_recommendation(stored.source_confirmation_id)
        final_plan = self._build_final_plan(decision_type, stored.recommendation, modified_plan_details or {})
        record_id = self.repository.next_evidence_id()
        evidence = {
            "record_id": record_id,
            "name": "GreenProof Evidence Record",
            "generated_at": datetime.fromisoformat(decided_at).isoformat(),
            "storage_mode": "in_memory",
            "original_request": to_dict(extraction_snapshot["request"]) if extraction_snapshot else None,
            "original_request_reference": extraction_snapshot["request"]["content_reference"] if extraction_snapshot else None,
            "extraction_result": extraction_snapshot["extraction"] if extraction_snapshot else None,
            "extraction_evidence": extraction_snapshot["evidence"] if extraction_snapshot else [],
            "confirmed_demand": to_dict(stored.demand),
            "resources_considered": [
                item.resource_id for item in self.dataset.material_resources
            ] + [
                item.resource_id for item in self.dataset.equipment_resources
            ] + [
                self.dataset.commercial_equipment_fallback.resource_id
            ],
            "resources_selected": [to_dict(item) for item in stored.recommendation.selected_material_resources],
            "selected_equipment": to_dict(stored.recommendation.selected_equipment),
            "resources_excluded": [to_dict(item) for item in stored.recommendation.excluded_resources],
            "exclusion_reasons": {
                item.resource_id: item.reason_text for item in stored.recommendation.excluded_resources
            },
            "assumptions": list(stored.recommendation.assumptions),
            "cost_comparison": to_dict(stored.recommendation.cost_breakdown),
            "carbon_comparison": to_dict(stored.recommendation.carbon_breakdown),
            "recommendation": to_dict(stored.recommendation),
            "user_decision": decision_payload,
            "overrides": [override_notes] if override_notes else [],
            "final_approved_plan": final_plan,
            "calculation_version": CALCULATION_VERSION,
            "provider_metadata": extraction_snapshot["provider_metadata"] if extraction_snapshot else None,
        }
        self.repository.evidence_records[record_id] = evidence
        
        # Persist if an evidence repository is available
        if self.evidence_repository is not None:
            self.evidence_repository.save(
                record_id=record_id,
                record_payload=evidence,
                decided_by=actor_reference,
                decided_at=decided_at,
                recommendation_id=stored.recommendation.recommendation_id,
            )
            
        return decision_payload, evidence

    def get_evidence_record(self, record_id: str) -> dict:
        if self.evidence_repository is not None:
            record = self.evidence_repository.get(record_id)
            if record is not None:
                return record
                
        record = self.repository.evidence_records.get(record_id)
        if record is None:
            raise ServiceError("EVIDENCE_RECORD_NOT_FOUND", "Evidence record was not found.", status_code=404)
        return record

    def _find_extraction_for_recommendation(self, confirmation_id: str | None) -> dict | None:
        if confirmation_id is None:
            return None
        confirmation = self.repository.confirmations.get(confirmation_id)
        if confirmation is None:
            return None
        matched = None
        for extraction_id, stored_extraction in self.repository.extractions.items():
            if stored_extraction.request.request_id == confirmation.request_id:
                matched = {
                    "extraction_id": extraction_id,
                    "request": to_dict(stored_extraction.request),
                    "extraction": to_dict(stored_extraction.extraction),
                    "evidence": [
                        to_dict(field.evidence_reference)
                        for field in stored_extraction.extraction.extracted_fields
                        if field.evidence_reference is not None
                    ],
                    "provider_metadata": to_dict(stored_extraction.extraction.model_metadata),
                }
                break
        return matched

    def _build_final_plan(self, decision_type: ApprovalDecisionType, recommendation, modified_plan_details: dict) -> dict:
        if decision_type == ApprovalDecisionType.APPROVE:
            return {"plan_type": "greenproof_recommendation", "recommendation_id": recommendation.recommendation_id}
        if decision_type == ApprovalDecisionType.MODIFY:
            return {
                "plan_type": "modified_greenproof_recommendation",
                "recommendation_id": recommendation.recommendation_id,
                "modified_plan_details": modified_plan_details,
            }
        if decision_type == ApprovalDecisionType.PROCEED_WITH_NORMAL_PROCUREMENT:
            return {"plan_type": "normal_procurement"}
        if decision_type == ApprovalDecisionType.REQUEST_INSPECTION:
            return {"plan_type": "inspection_requested"}
        return {"plan_type": "rejected"}
