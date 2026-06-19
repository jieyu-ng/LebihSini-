from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lebihsini_greenproof.ai_demo_fixtures import VOICE_NOTE_BM
from lebihsini_greenproof.ai_extraction import (
    ConfirmationInput,
    confirm_demand_extraction,
    extract_demand,
    generate_passport_from_resource_scan,
)
from lebihsini_greenproof.composer import generate_recommendation
from lebihsini_greenproof.contracts import ConfirmationAction, AIExtractionRequest, InputSourceType, ResourceKind
from lebihsini_greenproof.demo_data import load_demo_dataset
from lebihsini_greenproof.mock_grafilab_provider import MockGrafilabProvider
from lebihsini_greenproof.serialization import to_json_text


def main() -> None:
    dataset = load_demo_dataset()
    provider = MockGrafilabProvider()
    request = AIExtractionRequest(
        request_id="ai-demo-demand-001",
        source_type=InputSourceType.VOICE_NOTE,
        content=VOICE_NOTE_BM,
        content_reference="demo://voice-note/site-c/request-001",
        input_language="ms-MY",
        reference_datetime="2026-06-20T09:00:00+08:00",
    )
    extraction = extract_demand(request, provider)
    print("=== Structured Extraction ===")
    print(to_json_text(extraction))
    confirmation = confirm_demand_extraction(
        extraction,
        ConfirmationInput(
            request_id=request.request_id,
            action=ConfirmationAction.ACCEPT,
            confirmed_values={"product_code": "PG-600-GREY"},
            confirmed_at="2026-06-20T09:05:00+08:00",
        ),
    )
    print("=== Confirmed Demand ===")
    print(to_json_text(confirmation))
    recommendation = generate_recommendation(dataset, demand=confirmation.confirmed_demand)
    print("=== Final Recommendation ===")
    print(to_json_text(recommendation))
    _, site_e_passport = generate_passport_from_resource_scan(
        AIExtractionRequest(
            request_id="ai-demo-site-e-001",
            source_type=InputSourceType.RESOURCE_PHOTO,
            content="site e photo",
            content_reference="demo://resource/site-e-photo-001",
            input_language="en-MY",
        ),
        provider,
        ResourceKind.MATERIAL,
        dataset.material_resources[2],
    )
    print("=== Site E Provisional Passport ===")
    print(to_json_text(site_e_passport))


if __name__ == "__main__":
    main()
