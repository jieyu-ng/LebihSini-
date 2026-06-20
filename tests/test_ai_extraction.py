import os
import unittest
from dataclasses import replace

from lebihsini_greenproof.ai_demo_fixtures import ENGLISH_TYPED, VOICE_NOTE_BM
from lebihsini_greenproof.ai_extraction import (
    ConfirmationInput,
    confirm_demand_extraction,
    extract_demand,
    extract_resource_scan,
    generate_passport_from_resource_scan,
    run_confirmed_demand_to_recommendation,
)
from lebihsini_greenproof.contracts import (
    AIExtractionRequest,
    ConfidenceLabel,
    ConfirmationAction,
    ConfirmationStatus,
    InputSourceType,
    ResourceKind,
)
from lebihsini_greenproof.demo_data import load_demo_dataset
from lebihsini_greenproof.grafilab_client import GrafilabClient
from lebihsini_greenproof.mock_grafilab_provider import MockGrafilabProvider


class AIExtractionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = MockGrafilabProvider()
        self.dataset = load_demo_dataset()

    def test_bahasa_request_becomes_structured(self) -> None:
        result = extract_demand(
            AIExtractionRequest(
                request_id="bm-001",
                source_type=InputSourceType.VOICE_NOTE,
                content=VOICE_NOTE_BM,
                content_reference="demo://voice-note/site-c/request-001",
                input_language="ms-MY",
                reference_datetime="2026-06-20T09:00:00+08:00",
            ),
            self.provider,
        )
        self.assertEqual(result.detected_language, "ms-MY")
        self.assertEqual(result.normalized_demand["quantity_units"], 500)
        self.assertEqual(result.normalized_demand["equipment_duration_days"], 2)
        self.assertEqual(result.normalized_demand["deadline_at"], "2026-06-21T11:00:00+08:00")

    def test_english_request_becomes_structured(self) -> None:
        result = extract_demand(
            AIExtractionRequest(
                request_id="en-001",
                source_type=InputSourceType.TYPED_TEXT,
                content=ENGLISH_TYPED,
                content_reference="demo://typed/en/request-001",
                input_language="en-MY",
                reference_datetime="2026-06-20T09:00:00+08:00",
            ),
            self.provider,
        )
        self.assertEqual(result.detected_language, "en-MY")
        self.assertEqual(result.normalized_demand["dimension_mm_width"], 600)
        self.assertEqual(result.normalized_demand["dimension_mm_height"], 600)

    def test_malformed_provider_response_rejected(self) -> None:
        with self.assertRaises(ValueError):
            from lebihsini_greenproof.structured_output import validate_demand_provider_output

            validate_demand_provider_output(
                AIExtractionRequest(
                    request_id="bad-001",
                    source_type=InputSourceType.IMAGE,
                    content="bad",
                    content_reference="demo://bad",
                    input_language="en-MY",
                    reference_datetime="2026-06-20T09:00:00+08:00",
                ),
                {"provider_name": "mock"},
            )

    def test_unsupported_input_provider_failure(self) -> None:
        with self.assertRaises(Exception):
            extract_demand(
                AIExtractionRequest(
                    request_id="missing-001",
                    source_type=InputSourceType.IMAGE,
                    content="unknown",
                    content_reference="demo://missing",
                    input_language="en-MY",
                    reference_datetime="2026-06-20T09:00:00+08:00",
                ),
                self.provider,
            )

    def test_user_can_correct_ai_extracted_values(self) -> None:
        extraction = extract_demand(
            AIExtractionRequest(
                request_id="bm-002",
                source_type=InputSourceType.VOICE_NOTE,
                content=VOICE_NOTE_BM,
                content_reference="demo://voice-note/site-c/request-001",
                input_language="ms-MY",
                reference_datetime="2026-06-20T09:00:00+08:00",
            ),
            self.provider,
        )
        confirmed = confirm_demand_extraction(
            extraction,
            ConfirmationInput(
                request_id="bm-002",
                action=ConfirmationAction.EDIT,
                confirmed_values={"quantity_units": 520, "product_code": "PG-600-GREY"},
                confirmed_at="2026-06-20T09:05:00+08:00",
            ),
        )
        self.assertEqual(confirmed.status, ConfirmationStatus.CONFIRMED)
        self.assertEqual(confirmed.confirmed_demand.quantity_units, 520)

    def test_user_can_reject_extraction(self) -> None:
        extraction = extract_demand(
            AIExtractionRequest(
                request_id="bm-003",
                source_type=InputSourceType.VOICE_NOTE,
                content=VOICE_NOTE_BM,
                content_reference="demo://voice-note/site-c/request-001",
                input_language="ms-MY",
                reference_datetime="2026-06-20T09:00:00+08:00",
            ),
            self.provider,
        )
        confirmed = confirm_demand_extraction(
            extraction,
            ConfirmationInput(
                request_id="bm-003",
                action=ConfirmationAction.REJECT,
                confirmed_values={},
                confirmed_at="2026-06-20T09:05:00+08:00",
            ),
        )
        self.assertIsNone(confirmed.confirmed_demand)
        self.assertEqual(confirmed.status, ConfirmationStatus.REJECTED)

    def test_user_can_supply_missing_deadline(self) -> None:
        extraction = extract_demand(
            AIExtractionRequest(
                request_id="hand-002",
                source_type=InputSourceType.HANDWRITTEN_LIST,
                content="500 grey tiles 600x600",
                content_reference="demo://handwritten/request-001",
                input_language="en-MY",
                reference_datetime="2026-06-20T09:00:00+08:00",
            ),
            self.provider,
        )
        confirmed = confirm_demand_extraction(
            extraction,
            ConfirmationInput(
                request_id="hand-002",
                action=ConfirmationAction.PROVIDE,
                confirmed_values={
                    "deadline_at": "2026-06-21T11:00:00+08:00",
                    "product_code": "PG-600-GREY",
                },
                confirmed_at="2026-06-20T09:10:00+08:00",
            ),
        )
        self.assertEqual(confirmed.status, ConfirmationStatus.CONFIRMED)
        self.assertEqual(confirmed.confirmed_demand.deadline_at, "2026-06-21T11:00:00+08:00")

    def test_optimizer_receives_only_confirmed_values(self) -> None:
        extraction, confirmed, recommendation = run_confirmed_demand_to_recommendation(
            self.dataset,
            AIExtractionRequest(
                request_id="bm-004",
                source_type=InputSourceType.VOICE_NOTE,
                content=VOICE_NOTE_BM,
                content_reference="demo://voice-note/site-c/request-001",
                input_language="ms-MY",
                reference_datetime="2026-06-20T09:00:00+08:00",
            ),
            self.provider,
            ConfirmationInput(
                request_id="bm-004",
                action=ConfirmationAction.ACCEPT,
                confirmed_values={"product_code": "PG-600-GREY"},
                confirmed_at="2026-06-20T09:05:00+08:00",
            ),
        )
        self.assertIsNotNone(confirmed.confirmed_demand)
        self.assertEqual(recommendation.quantity_fulfilled_units, 500)
        self.assertTrue(extraction.extracted_fields)

    def test_site_a_material_passport_generation(self) -> None:
        extraction, result = generate_passport_from_resource_scan(
            AIExtractionRequest(
                request_id="site-a-001",
                source_type=InputSourceType.RESOURCE_PHOTO,
                content="site a",
                content_reference="demo://resource/site-a-photo-001",
                input_language="en-MY",
            ),
            self.provider,
            ResourceKind.MATERIAL,
            self.dataset.material_resources[0],
        )
        self.assertTrue(extraction.can_generate_passport)
        self.assertEqual(result.generated_material_passport.product_code, "PG-600-GREY")
        self.assertTrue(result.can_enter_automatic_matching)

    def test_site_e_provisional_passport_generation(self) -> None:
        _, result = generate_passport_from_resource_scan(
            AIExtractionRequest(
                request_id="site-e-001",
                source_type=InputSourceType.RESOURCE_PHOTO,
                content="site e",
                content_reference="demo://resource/site-e-photo-001",
                input_language="en-MY",
            ),
            self.provider,
            ResourceKind.MATERIAL,
            self.dataset.material_resources[2],
        )
        self.assertFalse(result.can_enter_automatic_matching)
        self.assertTrue(result.requires_manual_review)
        self.assertIn("could not be sufficiently verified", result.warnings[-1].message)

    def test_site_d_equipment_passport_generation(self) -> None:
        _, result = generate_passport_from_resource_scan(
            AIExtractionRequest(
                request_id="site-d-001",
                source_type=InputSourceType.RESOURCE_PHOTO,
                content="site d",
                content_reference="demo://resource/site-d-photo-001",
                input_language="en-MY",
            ),
            self.provider,
            ResourceKind.EQUIPMENT,
            self.dataset.equipment_resources[0],
        )
        self.assertEqual(result.generated_equipment_passport.brand_model, "Hilti DC-600 Demo")
        self.assertTrue(result.can_enter_automatic_matching)

    def test_incomplete_maintenance_evidence_requires_review(self) -> None:
        base = replace(self.dataset.equipment_resources[0], maintenance_confidence=0.5, maintenance_record_present=False)
        _, result = generate_passport_from_resource_scan(
            AIExtractionRequest(
                request_id="site-d-002",
                source_type=InputSourceType.RESOURCE_PHOTO,
                content="site d",
                content_reference="demo://resource/site-d-photo-001",
                input_language="en-MY",
            ),
            self.provider,
            ResourceKind.EQUIPMENT,
            base,
        )
        self.assertTrue(result.requires_manual_review)

    def test_provider_credentials_not_serialized(self) -> None:
        os.environ["GRAFILAB_API_KEY"] = "fixture-key-value"
        client = GrafilabClient()
        self.assertEqual(client.api_key, "fixture-key-value")
        from lebihsini_greenproof.serialization import to_jsonable

        serialized = to_jsonable({"provider_name": client.provider_name, "api_key_env_var": client.api_key_env_var})
        self.assertNotIn("fixture-key-value", str(serialized))

    def test_low_confidence_response_is_flagged(self) -> None:
        result = extract_demand(
            AIExtractionRequest(
                request_id="low-001",
                source_type=InputSourceType.IMAGE,
                content="blurred",
                content_reference="demo://low-confidence/request-001",
                input_language="unknown",
                reference_datetime="2026-06-20T09:00:00+08:00",
            ),
            self.provider,
        )
        self.assertFalse(result.can_proceed_to_confirmation)
        self.assertTrue(any(field.confidence_label == ConfidenceLabel.LOW for field in result.extracted_fields))


if __name__ == "__main__":
    unittest.main()
