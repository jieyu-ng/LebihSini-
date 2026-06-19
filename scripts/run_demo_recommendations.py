from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lebihsini_greenproof.composer import generate_recommendation
from lebihsini_greenproof.demo_data import load_demo_dataset
from lebihsini_greenproof.scenarios import SCENARIO_FIXTURES
from lebihsini_greenproof.serialization import to_json_text


def main() -> None:
    dataset = load_demo_dataset()
    tomorrow = generate_recommendation(
        dataset,
        scenario=SCENARIO_FIXTURES["tomorrow_deadline"].scenario,
    )
    three_hours = generate_recommendation(
        dataset,
        scenario=SCENARIO_FIXTURES["three_hour_deadline"].scenario,
    )
    print("=== Tomorrow Recommendation ===")
    print(to_json_text(tomorrow))
    print("=== Three-Hour Recommendation ===")
    print(to_json_text(three_hours))


if __name__ == "__main__":
    main()
