import unittest
from dataclasses import replace

from lebihsini_greenproof.composer import compose_material_plan, generate_recommendation
from lebihsini_greenproof.constraints import evaluate_material_candidate
from lebihsini_greenproof.demo_data import load_demo_dataset
from lebihsini_greenproof.equipment import MINIMUM_MAINTENANCE_CONFIDENCE
from lebihsini_greenproof.explanations import EXPLANATION_TEXT
from lebihsini_greenproof.scenarios import SCENARIO_FIXTURES
from lebihsini_greenproof.urgency import parse_iso_datetime, resolve_deadline_at


class OptimisationEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = load_demo_dataset()

    def test_material_category_mismatch(self) -> None:
        resource = replace(self.dataset.material_resources[0], category="cement")
        evaluation = evaluate_material_candidate(
            self.dataset.demand,
            resource,
            resolve_deadline_at(self.dataset.demand),
            self.dataset.material_collection_buffer_minutes,
        )
        self.assertFalse(evaluation.eligible)
        self.assertEqual(evaluation.exclusion.reason_code, "material_category_mismatch")

    def test_product_mismatch(self) -> None:
        resource = replace(self.dataset.material_resources[0], product_code="OTHER-CODE")
        evaluation = evaluate_material_candidate(
            self.dataset.demand,
            resource,
            resolve_deadline_at(self.dataset.demand),
            self.dataset.material_collection_buffer_minutes,
        )
        self.assertFalse(evaluation.eligible)
        self.assertEqual(evaluation.exclusion.reason_code, "product_code_mismatch")

    def test_dimension_mismatch(self) -> None:
        resource = replace(self.dataset.material_resources[0], dimension_mm_width=800)
        evaluation = evaluate_material_candidate(
            self.dataset.demand,
            resource,
            resolve_deadline_at(self.dataset.demand),
            self.dataset.material_collection_buffer_minutes,
        )
        self.assertFalse(evaluation.eligible)
        self.assertEqual(evaluation.exclusion.reason_code, "dimension_mismatch")

    def test_zero_quantity(self) -> None:
        resource = replace(self.dataset.material_resources[0], quantity_units=0)
        evaluation = evaluate_material_candidate(
            self.dataset.demand,
            resource,
            resolve_deadline_at(self.dataset.demand),
            self.dataset.material_collection_buffer_minutes,
        )
        self.assertFalse(evaluation.eligible)
        self.assertEqual(evaluation.exclusion.reason_code, "zero_quantity")

    def test_excessive_distance(self) -> None:
        resource = replace(self.dataset.material_resources[0], distance_to_site_km=99.0)
        evaluation = evaluate_material_candidate(
            self.dataset.demand,
            resource,
            resolve_deadline_at(self.dataset.demand),
            self.dataset.material_collection_buffer_minutes,
        )
        self.assertFalse(evaluation.eligible)
        self.assertEqual(evaluation.exclusion.reason_code, "distance_exceeded")

    def test_missed_deadline(self) -> None:
        resource = replace(self.dataset.material_resources[0], available_from_at="2026-06-21T11:30:00+08:00")
        evaluation = evaluate_material_candidate(
            self.dataset.demand,
            resource,
            resolve_deadline_at(self.dataset.demand),
            self.dataset.material_collection_buffer_minutes,
        )
        self.assertFalse(evaluation.eligible)
        self.assertEqual(evaluation.exclusion.reason_code, "available_too_late")

    def test_missing_documentation(self) -> None:
        resource = replace(self.dataset.material_resources[0], has_required_documentation=False)
        evaluation = evaluate_material_candidate(
            self.dataset.demand,
            resource,
            resolve_deadline_at(self.dataset.demand),
            self.dataset.material_collection_buffer_minutes,
        )
        self.assertFalse(evaluation.eligible)
        self.assertEqual(evaluation.exclusion.reason_code, "documentation_missing")

    def test_site_e_responsible_exclusion(self) -> None:
        resource = next(item for item in self.dataset.material_resources if item.site_id == "site-e")
        evaluation = evaluate_material_candidate(
            self.dataset.demand,
            resource,
            resolve_deadline_at(self.dataset.demand),
            self.dataset.material_collection_buffer_minutes,
        )
        self.assertFalse(evaluation.eligible)
        self.assertEqual(evaluation.exclusion.reason_code, "responsible_ai_policy")
        self.assertIn("could not be sufficiently verified", evaluation.exclusion.reason_text)
        self.assertNotIn("unsafe", evaluation.exclusion.reason_text.lower())

    def test_site_b_kept_with_inspection_condition(self) -> None:
        recommendation = generate_recommendation(
            self.dataset,
            scenario=SCENARIO_FIXTURES["tomorrow_deadline"].scenario,
        )
        site_b = next(item for item in recommendation.selected_material_resources if item.site_id == "site-b")
        self.assertTrue(site_b.inspection_required)
        self.assertEqual(site_b.conditions, [EXPLANATION_TEXT["inspection_required"]])
        self.assertEqual(
            recommendation.conditions.count(EXPLANATION_TEXT["inspection_required"]),
            1,
        )

    def test_tomorrow_scenario_exact_composition(self) -> None:
        recommendation = generate_recommendation(
            self.dataset,
            scenario=SCENARIO_FIXTURES["tomorrow_deadline"].scenario,
        )
        selected = {item.resource_id: item.quantity_units for item in recommendation.selected_material_resources}
        self.assertEqual(selected, {"mat-site-a-tiles": 300, "mat-site-b-tiles": 130})
        self.assertEqual(recommendation.supplier_shortfall_units, 70)
        self.assertEqual(recommendation.quantity_fulfilled_units, 500)
        self.assertEqual(recommendation.selected_equipment.resource_id, "eq-site-d-cutter")

    def test_no_source_over_allocation(self) -> None:
        result = compose_material_plan(
            self.dataset,
            self.dataset.demand,
            scenario=SCENARIO_FIXTURES["tomorrow_deadline"].scenario,
        )
        for item in result.selected_resources:
            source = next(resource for resource in self.dataset.material_resources if resource.resource_id == item.resource_id)
            self.assertLessEqual(item.quantity_units, source.quantity_units)

    def test_no_demand_over_allocation(self) -> None:
        result = compose_material_plan(
            self.dataset,
            self.dataset.demand,
            scenario=SCENARIO_FIXTURES["tomorrow_deadline"].scenario,
        )
        selected_total = sum(item.quantity_units for item in result.selected_resources)
        self.assertLessEqual(selected_total, self.dataset.demand.quantity_units)

    def test_no_eligible_reuse(self) -> None:
        recommendation = generate_recommendation(
            self.dataset,
            scenario=SCENARIO_FIXTURES["no_feasible_reuse"].scenario,
        )
        self.assertEqual(recommendation.selected_material_resources, [])
        self.assertEqual(recommendation.supplier_shortfall_units, 500)
        self.assertEqual(recommendation.verdict.value, "normal_procurement_recommended")

    def test_equipment_fallback_selected_when_site_d_unavailable(self) -> None:
        recommendation = generate_recommendation(
            self.dataset,
            scenario=SCENARIO_FIXTURES["equipment_unavailable"].scenario,
        )
        self.assertEqual(recommendation.selected_equipment.resource_id, "eq-commercial-fallback")
        self.assertTrue(recommendation.selected_equipment.is_commercial_fallback)

    def test_insufficient_maintenance_evidence(self) -> None:
        broken_dataset = replace(
            self.dataset,
            equipment_resources=[
                replace(self.dataset.equipment_resources[0], maintenance_confidence=MINIMUM_MAINTENANCE_CONFIDENCE - 0.1),
                *self.dataset.equipment_resources[1:],
            ],
        )
        recommendation = generate_recommendation(
            broken_dataset,
            scenario=SCENARIO_FIXTURES["tomorrow_deadline"].scenario,
        )
        excluded = {item.resource_id: item.reason_code for item in recommendation.excluded_resources}
        self.assertEqual(excluded["eq-site-d-cutter"], "maintenance_insufficient")

    def test_three_hour_scenario_comes_from_deadline_logic(self) -> None:
        recommendation = generate_recommendation(
            self.dataset,
            scenario=SCENARIO_FIXTURES["three_hour_deadline"].scenario,
        )
        selected = {item.resource_id: item.quantity_units for item in recommendation.selected_material_resources}
        self.assertEqual(selected, {"mat-site-a-tiles": 300})
        self.assertEqual(recommendation.supplier_shortfall_units, 200)
        excluded = {item.resource_id: item.reason_text for item in recommendation.excluded_resources}
        self.assertIn("mat-site-b-tiles", excluded)
        self.assertIn("cannot finish before the selected deadline", excluded["mat-site-b-tiles"].lower())

    def test_urgency_visibly_changes_plan(self) -> None:
        tomorrow = generate_recommendation(
            self.dataset,
            scenario=SCENARIO_FIXTURES["tomorrow_deadline"].scenario,
        )
        urgent = generate_recommendation(
            self.dataset,
            scenario=SCENARIO_FIXTURES["three_hour_deadline"].scenario,
        )
        self.assertNotEqual(
            [(item.resource_id, item.quantity_units) for item in tomorrow.selected_material_resources],
            [(item.resource_id, item.quantity_units) for item in urgent.selected_material_resources],
        )
        self.assertNotEqual(tomorrow.supplier_shortfall_units, urgent.supplier_shortfall_units)

    def test_financial_calculations_are_deterministic(self) -> None:
        recommendation = generate_recommendation(
            self.dataset,
            scenario=SCENARIO_FIXTURES["tomorrow_deadline"].scenario,
        )
        self.assertAlmostEqual(recommendation.cost_breakdown.normal_procurement_baseline_myr, 2650.0)
        self.assertAlmostEqual(recommendation.cost_breakdown.greenproof_total_myr, 2010.0)
        self.assertAlmostEqual(recommendation.cost_breakdown.net_saving_myr, 640.0)

    def test_carbon_calculations_are_deterministic(self) -> None:
        recommendation = generate_recommendation(
            self.dataset,
            scenario=SCENARIO_FIXTURES["tomorrow_deadline"].scenario,
        )
        self.assertAlmostEqual(recommendation.carbon_breakdown.baseline_carbon_kgco2e, 912.86)
        self.assertAlmostEqual(recommendation.carbon_breakdown.greenproof_carbon_kgco2e, 146.12)
        self.assertAlmostEqual(recommendation.carbon_breakdown.net_carbon_avoided_kgco2e, 766.74)

    def test_negative_carbon_benefit_handling(self) -> None:
        stressed_resources = [
            replace(
                resource,
                distance_to_site_km=24.0 if resource.site_id in {"site-a", "site-b"} else resource.distance_to_site_km,
            )
            for resource in self.dataset.material_resources
        ]
        stressed_dataset = replace(
            self.dataset,
            material_resources=stressed_resources,
            demand=replace(self.dataset.demand, maximum_distance_km=30.0),
            supplier_vehicle_factor_kgco2e_per_km=50.0,
        )
        recommendation = generate_recommendation(
            stressed_dataset,
            scenario=SCENARIO_FIXTURES["tomorrow_deadline"].scenario,
        )
        self.assertEqual(recommendation.selected_material_resources, [])
        self.assertEqual(recommendation.verdict.value, "normal_procurement_recommended")
        self.assertTrue(
            any(item.reason_code == "negative_net_carbon_benefit" for item in recommendation.excluded_resources)
        )

    def test_complete_contract_fields_and_reasoning_present(self) -> None:
        recommendation = generate_recommendation(
            self.dataset,
            scenario=SCENARIO_FIXTURES["tomorrow_deadline"].scenario,
        )
        self.assertTrue(recommendation.recommendation_id)
        self.assertTrue(recommendation.reasons)
        self.assertTrue(recommendation.assumptions)
        for item in recommendation.selected_material_resources:
            self.assertIsNotNone(item.resource_id)
        for item in recommendation.excluded_resources:
            self.assertTrue(item.reason_text)


if __name__ == "__main__":
    unittest.main()
