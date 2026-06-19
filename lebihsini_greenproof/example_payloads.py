from __future__ import annotations

from lebihsini_greenproof.contracts import (
    ApprovalDecisionType,
    EvidenceRecord,
    HumanApprovalDecision,
)
from lebihsini_greenproof.demo_data import load_demo_dataset
from lebihsini_greenproof.foundation import build_reference_recommendation
from lebihsini_greenproof.scenarios import SCENARIO_FIXTURES
from lebihsini_greenproof.serialization import to_jsonable


def build_example_payloads() -> dict[str, object]:
    dataset = load_demo_dataset()
    tomorrow = build_reference_recommendation(
        dataset,
        SCENARIO_FIXTURES["tomorrow_deadline"].scenario,
    )
    three_hours = build_reference_recommendation(
        dataset,
        SCENARIO_FIXTURES["three_hour_deadline"].scenario,
    )
    decision = HumanApprovalDecision(
        decision_id="decision-001",
        recommendation_id=tomorrow.recommendation_id,
        decision_type=ApprovalDecisionType.APPROVE,
        decided_by="demo.user@lebihsini.test",
        decided_at="2026-06-20T12:05:00+08:00",
        override_notes="Approved after confirming Site B inspection condition.",
    )
    evidence_record = EvidenceRecord(
        record_id="evidence-001",
        demand=dataset.demand,
        recommendation=tomorrow,
        original_request_reference="demo://voice-note/site-c/request-001",
        resources_considered=[item.resource_id for item in dataset.material_resources] + [item.resource_id for item in dataset.equipment_resources],
        human_decision=decision,
        overrides=[],
        expected_impact_summary="Reuse 430 tiles, purchase 70 new tiles, and use the nearby idle cutter while keeping the deadline feasible.",
        actual_outcome_summary=None,
    )
    return {
        "demand_request": to_jsonable(dataset.demand),
        "material_resource_passport": to_jsonable(dataset.material_resources[0]),
        "equipment_resource_passport": to_jsonable(dataset.equipment_resources[0]),
        "recommendation_response_tomorrow": to_jsonable(tomorrow),
        "recommendation_response_three_hours": to_jsonable(three_hours),
        "evidence_record": to_jsonable(evidence_record),
    }
