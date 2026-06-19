import json
import unittest

from datetime import datetime

from lebihsini_greenproof.contracts import (
    ApprovalDecisionType,
    EvidenceRecord,
    HumanApprovalDecision,
)
from lebihsini_greenproof.demo_data import load_demo_dataset
from lebihsini_greenproof.foundation import build_reference_recommendation
from lebihsini_greenproof.scenarios import SCENARIO_FIXTURES
from lebihsini_greenproof.serialization import to_json_text, to_jsonable


class SerializationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = load_demo_dataset()
        self.recommendation = build_reference_recommendation(
            self.dataset,
            SCENARIO_FIXTURES["tomorrow_deadline"].scenario,
        )

    def test_demand_request_serializes(self) -> None:
        payload = to_jsonable(self.dataset.demand)
        self.assertEqual(payload["quantity_units"], 500)
        json.loads(to_json_text(self.dataset.demand))

    def test_material_passport_serializes(self) -> None:
        payload = to_jsonable(self.dataset.material_resources[0])
        self.assertEqual(payload["site_id"], "site-a")
        json.loads(to_json_text(self.dataset.material_resources[0]))

    def test_equipment_passport_serializes(self) -> None:
        payload = to_jsonable(self.dataset.equipment_resources[0])
        self.assertEqual(payload["category"], "tile_cutter")
        json.loads(to_json_text(self.dataset.equipment_resources[0]))

    def test_recommendation_output_serializes(self) -> None:
        payload = to_jsonable(self.recommendation)
        self.assertEqual(payload["supplier_shortfall_units"], 70)
        json.loads(to_json_text(self.recommendation))

    def test_evidence_record_serializes(self) -> None:
        decision = HumanApprovalDecision(
            decision_id="decision-001",
            recommendation_id=self.recommendation.recommendation_id,
            decision_type=ApprovalDecisionType.APPROVE,
            decided_by="demo.user@lebihsini.test",
            decided_at="2026-06-20T12:05:00+08:00",
        )
        record = EvidenceRecord(
            record_id="record-001",
            demand=self.dataset.demand,
            recommendation=self.recommendation,
            original_request_reference="demo://request/001",
            resources_considered=["mat-site-a-tiles", "mat-site-b-tiles", "eq-site-d-cutter"],
            human_decision=decision,
            overrides=[],
            expected_impact_summary="Demo evidence record.",
        )
        payload = to_jsonable(record)
        self.assertEqual(payload["human_decision"]["decision_type"], "approve")
        json.loads(to_json_text(record))

    def test_datetime_serializes_to_iso8601(self) -> None:
        payload = to_jsonable({"when": datetime(2026, 6, 20, 12, 30, 0)})
        self.assertEqual(payload["when"], "2026-06-20T12:30:00")


if __name__ == "__main__":
    unittest.main()
