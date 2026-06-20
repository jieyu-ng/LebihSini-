import unittest

from lebihsini_greenproof.contracts import DemandRequest, RiskCategory, to_dict
from lebihsini_greenproof.demo_data import load_demo_dataset


class ContractTests(unittest.TestCase):
    def test_demand_request_rejects_invalid_confidence(self) -> None:
        with self.assertRaises(ValueError):
            DemandRequest(
                demand_id="bad",
                requesting_site_id="site-c",
                material_category="porcelain_tile",
                product_code="PG-600-GREY",
                colour="grey",
                dimension_mm_width=600,
                dimension_mm_height=600,
                quantity_units=500,
                deadline_at="2026-06-21T11:00:00+08:00",
                equipment_category="tile_cutter",
                equipment_duration_days=2,
                maximum_distance_km=25.0,
                maximum_risk=RiskCategory.AMBER,
                extraction_confidence=1.2,
                input_language="ms-MY",
                source_type="voice_note",
            )

    def test_demo_dataset_serializes(self) -> None:
        dataset = load_demo_dataset()
        serialized = to_dict(dataset.demand)
        self.assertEqual(serialized["product_code"], "PG-600-GREY")


if __name__ == "__main__":
    unittest.main()
