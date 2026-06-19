import json
import unittest
from pathlib import Path

from lebihsini_greenproof.example_payloads import build_example_payloads
from lebihsini_greenproof.serialization import to_jsonable


class ExampleFileTests(unittest.TestCase):
    def test_example_files_parse_and_match_generated_payloads(self) -> None:
        root = Path(__file__).resolve().parents[1]
        examples_dir = root / "examples"
        expected = build_example_payloads()
        file_map = {
            "demand_request": "demand_request.json",
            "material_resource_passport": "material_resource_passport.json",
            "equipment_resource_passport": "equipment_resource_passport.json",
            "recommendation_response_tomorrow": "recommendation_response_tomorrow.json",
            "recommendation_response_three_hours": "recommendation_response_three_hours.json",
            "evidence_record": "evidence_record.json",
        }
        for key, filename in file_map.items():
            with self.subTest(filename=filename):
                payload = json.loads((examples_dir / filename).read_text(encoding="utf-8"))
                self.assertEqual(payload, to_jsonable(expected[key]))


if __name__ == "__main__":
    unittest.main()
