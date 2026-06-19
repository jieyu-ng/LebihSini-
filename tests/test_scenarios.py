import unittest

from lebihsini_greenproof.demo_data import load_demo_dataset
from lebihsini_greenproof.explanations import EXPLANATION_TEXT
from lebihsini_greenproof.foundation import build_reference_recommendation
from lebihsini_greenproof.scenarios import SCENARIO_FIXTURES


class ScenarioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = load_demo_dataset()

    def test_tomorrow_deadline(self) -> None:
        fixture = SCENARIO_FIXTURES["tomorrow_deadline"]
        recommendation = build_reference_recommendation(self.dataset, fixture.scenario)
        self.assertEqual(
            tuple(item.resource_id for item in recommendation.selected_material_resources),
            fixture.expected_material_ids,
        )
        self.assertEqual(recommendation.supplier_shortfall_units, 70)
        self.assertEqual(recommendation.quantity_fulfilled_units, 500)
        self.assertEqual(recommendation.selected_equipment.resource_id, "eq-site-d-cutter")
        self.assertIn(EXPLANATION_TEXT["inspection_required"], recommendation.conditions)
        excluded_ids = {item.resource_id for item in recommendation.excluded_resources}
        self.assertTrue(set(fixture.expected_excluded_ids).issubset(excluded_ids))

    def test_three_hour_deadline(self) -> None:
        fixture = SCENARIO_FIXTURES["three_hour_deadline"]
        recommendation = build_reference_recommendation(self.dataset, fixture.scenario)
        self.assertEqual(
            tuple(item.resource_id for item in recommendation.selected_material_resources),
            fixture.expected_material_ids,
        )
        self.assertEqual(recommendation.supplier_shortfall_units, 200)
        excluded_map = {item.resource_id: item.reason_text for item in recommendation.excluded_resources}
        self.assertIn("mat-site-b-tiles", excluded_map)
        self.assertIn("delivery deadline", excluded_map["mat-site-b-tiles"].lower())

    def test_site_e_unreadable_label_case(self) -> None:
        fixture = SCENARIO_FIXTURES["site_e_unreadable"]
        recommendation = build_reference_recommendation(self.dataset, fixture.scenario)
        excluded_map = {item.resource_id: item.reason_text for item in recommendation.excluded_resources}
        self.assertIn("mat-site-e-tiles", excluded_map)
        self.assertIn("could not be sufficiently verified", excluded_map["mat-site-e-tiles"])
        self.assertNotIn("unsafe", excluded_map["mat-site-e-tiles"].lower())

    def test_no_feasible_reuse_case(self) -> None:
        fixture = SCENARIO_FIXTURES["no_feasible_reuse"]
        recommendation = build_reference_recommendation(self.dataset, fixture.scenario)
        self.assertEqual(recommendation.selected_material_resources, [])
        self.assertEqual(recommendation.supplier_shortfall_units, 500)
        self.assertEqual(recommendation.quantity_fulfilled_units, 500)
        self.assertIn("normal procurement recommended", recommendation.reasons[0].lower())

    def test_equipment_unavailable_case(self) -> None:
        fixture = SCENARIO_FIXTURES["equipment_unavailable"]
        recommendation = build_reference_recommendation(self.dataset, fixture.scenario)
        self.assertIsNone(recommendation.selected_equipment)
        excluded_ids = {item.resource_id for item in recommendation.excluded_resources}
        self.assertIn("eq-site-d-cutter", excluded_ids)

    def test_supplier_fallback_exact_total(self) -> None:
        fixture = SCENARIO_FIXTURES["supplier_fallback_exact_total"]
        recommendation = build_reference_recommendation(self.dataset, fixture.scenario)
        selected_total = sum(item.quantity_units for item in recommendation.selected_material_resources)
        self.assertEqual(selected_total + recommendation.supplier_shortfall_units, self.dataset.demand.quantity_units)
        self.assertEqual(recommendation.supplier_shortfall_units, fixture.expected_supplier_shortfall_units)


if __name__ == "__main__":
    unittest.main()
