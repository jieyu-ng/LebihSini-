from __future__ import annotations

from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lebihsini_greenproof.ai_extraction import extract_demand
from lebihsini_greenproof.contracts import AIExtractionRequest, InputSourceType
from lebihsini_greenproof.grafilab_client import GrafilabClient
from lebihsini_greenproof.serialization import to_json_text


def main() -> int:
    if not os.getenv("GRAFILAB_API_KEY"):
        print("Real Grafilab smoke test skipped because GRAFILAB_API_KEY is not set.")
        return 0
    print("Running a real Grafilab network smoke test with typed text only.")
    client = GrafilabClient()
    result = extract_demand(
        AIExtractionRequest(
            request_id="grafilab-smoke-001",
            source_type=InputSourceType.TYPED_TEXT,
            content="Esok perlukan 500 tile kelabu 600 kali 600 dan mesin pemotong untuk dua hari.",
            content_reference="text://grafilab-smoke-test",
            input_language="ms-MY",
            reference_datetime="2026-06-20T09:00:00+08:00",
        ),
        client,
    )
    print(to_json_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
