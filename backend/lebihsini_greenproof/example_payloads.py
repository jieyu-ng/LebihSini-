from __future__ import annotations

from lebihsini_greenproof.contracts import (
    ApprovalDecisionType,
    AIExtractionRequest,
    AIProviderError,
    ConfirmationAction,
    EvidenceRecord,
    HumanApprovalDecision,
    InputSourceType,
    ResourceKind,
)
from lebihsini_greenproof.ai_extraction import (
    ConfirmationInput,
    confirm_demand_extraction,
    extract_demand,
    generate_passport_from_resource_scan,
)
from lebihsini_greenproof.ai_demo_fixtures import ENGLISH_TYPED, VOICE_NOTE_BM
from lebihsini_greenproof.composer import generate_recommendation
from lebihsini_greenproof.demo_data import load_demo_dataset
from lebihsini_greenproof.mock_grafilab_provider import MockGrafilabProvider
from lebihsini_greenproof.scenarios import SCENARIO_FIXTURES
from lebihsini_greenproof.serialization import to_jsonable


def build_example_payloads() -> dict[str, object]:
    dataset = load_demo_dataset()
    provider = MockGrafilabProvider()
    tomorrow = generate_recommendation(
        dataset,
        scenario=SCENARIO_FIXTURES["tomorrow_deadline"].scenario,
    )
    three_hours = generate_recommendation(
        dataset,
        scenario=SCENARIO_FIXTURES["three_hour_deadline"].scenario,
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
        resources_considered=[item.resource_id for item in dataset.material_resources]
        + [item.resource_id for item in dataset.equipment_resources]
        + [dataset.commercial_equipment_fallback.resource_id],
        human_decision=decision,
        overrides=[],
        expected_impact_summary="Reuse 430 tiles, purchase 70 new tiles, and use the nearby idle cutter while keeping the deadline feasible.",
        actual_outcome_summary=None,
    )
    bm_request = AIExtractionRequest(
        request_id="extract-bm-001",
        source_type=InputSourceType.VOICE_NOTE,
        content=VOICE_NOTE_BM,
        content_reference="demo://voice-note/site-c/request-001",
        input_language="ms-MY",
        reference_datetime="2026-06-20T09:00:00+08:00",
    )
    english_request = AIExtractionRequest(
        request_id="extract-en-001",
        source_type=InputSourceType.TYPED_TEXT,
        content=ENGLISH_TYPED,
        content_reference="demo://typed/en/request-001",
        input_language="en-MY",
        reference_datetime="2026-06-20T09:00:00+08:00",
    )
    handwritten_request = AIExtractionRequest(
        request_id="extract-handwritten-001",
        source_type=InputSourceType.HANDWRITTEN_LIST,
        content="500 grey tiles 600x600",
        content_reference="demo://handwritten/request-001",
        input_language="en-MY",
        reference_datetime="2026-06-20T09:00:00+08:00",
    )
    bm_extraction = extract_demand(bm_request, provider)
    english_extraction = extract_demand(english_request, provider)
    correction_extraction = extract_demand(handwritten_request, provider)
    confirmed = confirm_demand_extraction(
        bm_extraction,
        ConfirmationInput(
            request_id=bm_extraction.request_id,
            action=ConfirmationAction.ACCEPT,
            confirmed_values={"product_code": "PG-600-GREY"},
            confirmed_at="2026-06-20T09:05:00+08:00",
        ),
    )
    site_a_passport = generate_passport_from_resource_scan(
        AIExtractionRequest(
            request_id="resource-site-a-001",
            source_type=InputSourceType.RESOURCE_PHOTO,
            content="site a photo",
            content_reference="demo://resource/site-a-photo-001",
            input_language="en-MY",
        ),
        provider,
        ResourceKind.MATERIAL,
        dataset.material_resources[0],
    )[1]
    site_e_passport = generate_passport_from_resource_scan(
        AIExtractionRequest(
            request_id="resource-site-e-001",
            source_type=InputSourceType.RESOURCE_PHOTO,
            content="site e photo",
            content_reference="demo://resource/site-e-photo-001",
            input_language="en-MY",
        ),
        provider,
        ResourceKind.MATERIAL,
        dataset.material_resources[2],
    )[1]
    site_d_passport = generate_passport_from_resource_scan(
        AIExtractionRequest(
            request_id="resource-site-d-001",
            source_type=InputSourceType.RESOURCE_PHOTO,
            content="site d photo",
            content_reference="demo://resource/site-d-photo-001",
            input_language="en-MY",
        ),
        provider,
        ResourceKind.EQUIPMENT,
        dataset.equipment_resources[0],
    )[1]
    provider_error = AIProviderError(
        code="AI_PROVIDER_UNAVAILABLE",
        message="Mocked provider outage for contract example.",
        retryable=True,
        provider_name="mock_grafilab",
    )
    return {
        "demand_request": to_jsonable(dataset.demand),
        "bahasa_voice_extraction": to_jsonable(bm_extraction),
        "image_extraction": to_jsonable(english_extraction),
        "extraction_requires_correction": to_jsonable(correction_extraction),
        "confirmed_demand": to_jsonable(confirmed),
        "material_resource_passport": to_jsonable(dataset.material_resources[0]),
        "equipment_resource_passport": to_jsonable(dataset.equipment_resources[0]),
        "site_a_material_passport": to_jsonable(site_a_passport),
        "site_e_provisional_passport": to_jsonable(site_e_passport),
        "site_d_equipment_passport": to_jsonable(site_d_passport),
        "grafilab_provider_error": to_jsonable(provider_error),
        "low_confidence_response": to_jsonable(
            extract_demand(
                AIExtractionRequest(
                    request_id="extract-low-001",
                    source_type=InputSourceType.IMAGE,
                    content="blurred scan",
                    content_reference="demo://low-confidence/request-001",
                    input_language="unknown",
                    reference_datetime="2026-06-20T09:00:00+08:00",
                ),
                provider,
            )
        ),
        "recommendation_response_tomorrow": to_jsonable(tomorrow),
        "recommendation_response_three_hours": to_jsonable(three_hours),
        "evidence_record": to_jsonable(evidence_record),
    }
