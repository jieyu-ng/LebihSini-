from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lebihsini_greenproof.example_payloads import build_example_payloads
from lebihsini_greenproof.serialization import to_json_text


def main() -> None:
    examples_dir = ROOT / "examples"
    examples_dir.mkdir(exist_ok=True)
    payloads = build_example_payloads()
    file_map = {
        "demand_request": "demand_request.json",
        "material_resource_passport": "material_resource_passport.json",
        "equipment_resource_passport": "equipment_resource_passport.json",
        "recommendation_response_tomorrow": "recommendation_response_tomorrow.json",
        "recommendation_response_three_hours": "recommendation_response_three_hours.json",
        "evidence_record": "evidence_record.json",
    }
    for key, filename in file_map.items():
        (examples_dir / filename).write_text(to_json_text(payloads[key]) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
