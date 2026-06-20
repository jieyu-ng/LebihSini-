import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from lebihsini_greenproof.api.app import create_app


class BackendApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.app.state.repository.reset()
        
        # Reseed demo resources because reset() clears them
        dataset = self.app.state.dataset
        for m in dataset.material_resources:
            self.app.state.repository.material_passports[m.resource_id] = m
        for e in dataset.equipment_resources:
            self.app.state.repository.equipment_passports[e.resource_id] = e
        self.app.state.repository.equipment_passports[dataset.commercial_equipment_fallback.resource_id] = dataset.commercial_equipment_fallback
        
        self.client = TestClient(self.app)

    def test_health_reports_provider_mode_without_secrets(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["provider_mode"], "mock")
        self.assertEqual(body["storage_mode"], "in_memory")
        self.assertEqual(body["provider_model"], "mock_grafilab")
        self.assertNotIn("api_key", str(body).lower())

    def test_health_reports_grafilab_mode_without_revealing_credentials(self) -> None:
        with patch.dict("os.environ", {"GREENPROOF_PROVIDER_MODE": "grafilab", "GRAFILAB_API_KEY": ""}, clear=False):
            app = create_app()
            client = TestClient(app)
            response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["provider_mode"], "grafilab")
        self.assertFalse(body["provider_configured"])
        self.assertEqual(body["provider_model"], "grafilab/qwen3.6-flash")
        self.assertNotIn("api_key", str(body).lower())

    def test_grafilab_mode_without_key_fails_clearly(self) -> None:
        with patch.dict("os.environ", {"GREENPROOF_PROVIDER_MODE": "grafilab", "GRAFILAB_API_KEY": ""}, clear=False):
            app = create_app()
            client = TestClient(app)
            response = client.post(
                "/api/extract-request",
                json={
                    "request_id": "real-missing-key-001",
                    "source_type": "typed_text",
                    "content": "Need 500 grey porcelain tiles 600x600 tomorrow and a tile cutter for two days.",
                    "content_reference": "text://typed/en/request-001",
                    "input_language": "en-MY",
                    "reference_datetime": "2026-06-20T09:00:00+08:00",
                },
            )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"]["code"], "AI_PROVIDER_UNAVAILABLE")

    def test_bahasa_fixture_extraction(self) -> None:
        response = self.client.post(
            "/api/extract-request",
            json={
                "request_id": "bm-001",
                "source_type": "voice_note",
                "content": "Esok perlukan 500 tile kelabu 600 kali 600 dan mesin pemotong untuk dua hari.",
                "content_reference": "demo://voice-note/site-c/request-001",
                "input_language": "ms-MY",
                "reference_datetime": "2026-06-20T09:00:00+08:00",
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["normalized_demand"]["quantity_units"], 500)
        self.assertEqual(body["confirmation_status"], "pending")

    def test_typed_english_extraction(self) -> None:
        response = self.client.post(
            "/api/extract-request",
            json={
                "request_id": "en-001",
                "source_type": "typed_text",
                "content": "Need 500 grey porcelain tiles 600x600 tomorrow and a tile cutter for two days.",
                "content_reference": "demo://typed/en/request-001",
                "input_language": "en-MY",
                "reference_datetime": "2026-06-20T09:00:00+08:00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detected_language"], "en-MY")

    def test_unsupported_input_type_returns_standard_error(self) -> None:
        response = self.client.post(
            "/api/extract-request",
            json={
                "request_id": "bad-001",
                "source_type": "video_file",
                "content": "bad",
                "content_reference": "demo://bad",
            },
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "UNSUPPORTED_INPUT_TYPE")

    def test_unreadable_input_returns_standard_error(self) -> None:
        response = self.client.post(
            "/api/extract-request",
            json={
                "request_id": "bad-002",
                "source_type": "image",
                "content": "bad",
                "content_reference": "demo://missing",
                "input_language": "en-MY",
                "reference_datetime": "2026-06-20T09:00:00+08:00",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "INPUT_UNREADABLE")

    def test_low_confidence_response_still_returns_structured_payload(self) -> None:
        response = self.client.post(
            "/api/extract-request",
            json={
                "request_id": "low-001",
                "source_type": "image",
                "content": "blurred scan",
                "content_reference": "demo://low-confidence/request-001",
                "input_language": "unknown",
                "reference_datetime": "2026-06-20T09:00:00+08:00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["can_proceed_to_confirmation"])

    def test_accept_extraction(self) -> None:
        extraction_id = self._create_demo_extraction()
        response = self.client.post(
            f"/api/extractions/{extraction_id}/confirm",
            json={
                "action": "accept",
                "confirmed_values": {"product_code": "PG-600-GREY"},
                "confirmed_at": "2026-06-20T09:05:00+08:00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "confirmed")

    def test_edit_quantity(self) -> None:
        extraction_id = self._create_demo_extraction()
        response = self.client.post(
            f"/api/extractions/{extraction_id}/confirm",
            json={
                "action": "edit",
                "confirmed_values": {"quantity_units": 520, "product_code": "PG-600-GREY"},
                "confirmed_at": "2026-06-20T09:05:00+08:00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["confirmed_demand"]["quantity_units"], 520)

    def test_supply_missing_deadline(self) -> None:
        response = self.client.post(
            "/api/extract-request",
            json={
                "request_id": "hand-001",
                "source_type": "handwritten_list",
                "content": "500 grey tiles 600x600",
                "content_reference": "demo://handwritten/request-001",
                "input_language": "en-MY",
                "reference_datetime": "2026-06-20T09:00:00+08:00",
            },
        )
        extraction_id = response.json()["extraction_id"]
        confirm = self.client.post(
            f"/api/extractions/{extraction_id}/confirm",
            json={
                "action": "provide",
                "confirmed_values": {
                    "deadline_at": "2026-06-21T11:00:00+08:00",
                    "product_code": "PG-600-GREY",
                },
                "confirmed_at": "2026-06-20T09:10:00+08:00",
            },
        )
        self.assertEqual(confirm.status_code, 200)
        self.assertEqual(confirm.json()["status"], "confirmed")

    def test_reject_extraction(self) -> None:
        extraction_id = self._create_demo_extraction()
        response = self.client.post(
            f"/api/extractions/{extraction_id}/confirm",
            json={
                "action": "reject",
                "confirmed_values": {},
                "confirmed_at": "2026-06-20T09:05:00+08:00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "rejected")

    def test_unresolved_critical_field_blocked(self) -> None:
        response = self.client.post(
            "/api/extract-request",
            json={
                "request_id": "hand-002",
                "source_type": "handwritten_list",
                "content": "500 grey tiles 600x600",
                "content_reference": "demo://handwritten/request-001",
                "input_language": "en-MY",
                "reference_datetime": "2026-06-20T09:00:00+08:00",
            },
        )
        extraction_id = response.json()["extraction_id"]
        confirm = self.client.post(
            f"/api/extractions/{extraction_id}/confirm",
            json={
                "action": "accept",
                "confirmed_values": {},
                "confirmed_at": "2026-06-20T09:05:00+08:00",
            },
        )
        self.assertEqual(confirm.status_code, 409)
        self.assertEqual(confirm.json()["error"]["code"], "MISSING_CRITICAL_FIELD")

    def test_site_a_material_passport(self) -> None:
        response = self.client.post(
            "/api/material-passports",
            json={
                "request_id": "site-a-001",
                "source_type": "resource_photo",
                "content": "site a",
                "content_reference": "demo://resource/site-a-photo-001",
                "input_language": "en-MY",
                "resource_id": "mat-site-a-tiles",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["can_enter_automatic_matching"])

    def test_site_e_provisional_passport(self) -> None:
        response = self.client.post(
            "/api/material-passports",
            json={
                "request_id": "site-e-001",
                "source_type": "resource_photo",
                "content": "site e",
                "content_reference": "demo://resource/site-e-photo-001",
                "input_language": "en-MY",
                "resource_id": "mat-site-e-tiles",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["requires_manual_review"])

    def test_site_d_equipment_passport(self) -> None:
        response = self.client.post(
            "/api/equipment-passports",
            json={
                "request_id": "site-d-001",
                "source_type": "resource_photo",
                "content": "site d",
                "content_reference": "demo://resource/site-d-photo-001",
                "input_language": "en-MY",
                "resource_id": "eq-site-d-cutter",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["can_enter_automatic_matching"])

    def test_missing_resource_returns_standard_error(self) -> None:
        response = self.client.get("/api/resources/does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "RESOURCE_NOT_FOUND")

    def test_confirmed_demand_required_for_recommendation(self) -> None:
        response = self.client.post("/api/recommendations", json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "MISSING_CRITICAL_FIELD")

    def test_tomorrow_composition_and_breakdowns(self) -> None:
        confirmation_id = self._confirm_demo_extraction()
        response = self.client.post(
            "/api/recommendations",
            json={"confirmed_demand_id": confirmation_id},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        selected = {item["site_id"]: item["quantity_units"] for item in body["selected_material_resources"]}
        self.assertEqual(selected, {"site-a": 300, "site-b": 130})
        self.assertEqual(body["supplier_shortfall_units"], 70)
        self.assertEqual(body["selected_equipment"]["resource_id"], "eq-site-d-cutter")
        self.assertIn("mat-site-e-tiles", {item["resource_id"] for item in body["excluded_resources"]})
        self.assertTrue(body["cost_breakdown"])
        self.assertTrue(body["carbon_breakdown"])
        self.assertIn("inspection", " ".join(body["conditions"]).lower())

    def test_urgency_recalculation_produces_300_plus_200(self) -> None:
        confirmation_id = self._confirm_demo_extraction()
        recommendation = self.client.post(
            "/api/recommendations",
            json={"confirmed_demand_id": confirmation_id},
        ).json()
        response = self.client.post(
            f"/api/recommendations/{recommendation['recommendation_id']}/recalculate",
            json={"revised_deadline_at": "2026-06-21T09:30:00+08:00"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        selected = {item["site_id"]: item["quantity_units"] for item in body["selected_material_resources"]}
        self.assertEqual(selected, {"site-a": 300})
        self.assertEqual(body["supplier_shortfall_units"], 200)
        excluded = {item["resource_id"]: item["reason_text"] for item in body["excluded_resources"]}
        self.assertIn("mat-site-b-tiles", excluded)

    def test_decision_and_evidence_record(self) -> None:
        confirmation_id = self._confirm_demo_extraction()
        recommendation = self.client.post(
            "/api/recommendations",
            json={"confirmed_demand_id": confirmation_id},
        ).json()
        decision = self.client.post(
            f"/api/recommendations/{recommendation['recommendation_id']}/decision",
            json={
                "decision_type": "approve",
                "actor_reference": "demo.user@lebihsini.test",
                "decided_at": "2026-06-20T12:05:00+08:00",
                "override_notes": "Approved after review.",
            },
        )
        self.assertEqual(decision.status_code, 200)
        decision_body = decision.json()
        evidence = self.client.get(f"/api/evidence-records/{decision_body['evidence_record']['record_id']}")
        self.assertEqual(evidence.status_code, 200)
        evidence_body = evidence.json()
        self.assertEqual(evidence_body["name"], "GreenProof Evidence Record")
        self.assertNotIn("certificate", str(evidence_body).lower())

    def test_request_inspection_decision(self) -> None:
        confirmation_id = self._confirm_demo_extraction()
        recommendation = self.client.post(
            "/api/recommendations",
            json={"confirmed_demand_id": confirmation_id},
        ).json()
        decision = self.client.post(
            f"/api/recommendations/{recommendation['recommendation_id']}/decision",
            json={
                "decision_type": "request_inspection",
                "actor_reference": "demo.user@lebihsini.test",
                "decided_at": "2026-06-20T12:05:00+08:00",
            },
        )
        self.assertEqual(decision.status_code, 200)
        self.assertEqual(
            decision.json()["evidence_record"]["final_approved_plan"]["plan_type"],
            "inspection_requested",
        )

    def test_repository_reset_isolated(self) -> None:
        self._confirm_demo_extraction()
        self.app.state.repository.reset()
        resources = self.client.get("/api/resources").json()
        self.assertEqual(resources["count"], 7)

    def _create_demo_extraction(self) -> str:
        response = self.client.post(
            "/api/extract-request",
            json={
                "request_id": "bm-setup",
                "source_type": "voice_note",
                "content": "Esok perlukan 500 tile kelabu 600 kali 600 dan mesin pemotong untuk dua hari.",
                "content_reference": "demo://voice-note/site-c/request-001",
                "input_language": "ms-MY",
                "reference_datetime": "2026-06-20T09:00:00+08:00",
            },
        )
        return response.json()["extraction_id"]

    def _confirm_demo_extraction(self) -> str:
        extraction_id = self._create_demo_extraction()
        response = self.client.post(
            f"/api/extractions/{extraction_id}/confirm",
            json={
                "action": "accept",
                "confirmed_values": {"product_code": "PG-600-GREY"},
                "confirmed_at": "2026-06-20T09:05:00+08:00",
            },
        )
        return response.json()["confirmation_id"]


if __name__ == "__main__":
    unittest.main()
