from __future__ import annotations

from dataclasses import dataclass

from lebihsini_greenproof.urgency import RecommendationScenario


@dataclass(slots=True)
class ScenarioExpectation:
    scenario: RecommendationScenario
    expected_material_ids: tuple[str, ...]
    expected_excluded_ids: tuple[str, ...]
    expected_supplier_shortfall_units: int
    expected_equipment_id: str | None


SCENARIO_FIXTURES = {
    "tomorrow_deadline": ScenarioExpectation(
        scenario=RecommendationScenario(
            scenario_id="tomorrow-deadline",
        ),
        expected_material_ids=("mat-site-a-tiles", "mat-site-b-tiles"),
        expected_excluded_ids=("mat-site-e-tiles", "mat-site-g-wrong-size", "eq-site-h-unavailable"),
        expected_supplier_shortfall_units=70,
        expected_equipment_id="eq-site-d-cutter",
    ),
    "three_hour_deadline": ScenarioExpectation(
        scenario=RecommendationScenario(
            scenario_id="three-hour-deadline",
            revised_deadline_at="2026-06-21T09:30:00+08:00",
        ),
        expected_material_ids=("mat-site-a-tiles",),
        expected_excluded_ids=("mat-site-b-tiles", "mat-site-e-tiles", "mat-site-g-wrong-size", "eq-site-h-unavailable"),
        expected_supplier_shortfall_units=200,
        expected_equipment_id="eq-site-d-cutter",
    ),
    "site_e_unreadable": ScenarioExpectation(
        scenario=RecommendationScenario(
            scenario_id="site-e-unreadable",
        ),
        expected_material_ids=("mat-site-a-tiles", "mat-site-b-tiles"),
        expected_excluded_ids=("mat-site-e-tiles", "mat-site-g-wrong-size", "eq-site-h-unavailable"),
        expected_supplier_shortfall_units=70,
        expected_equipment_id="eq-site-d-cutter",
    ),
    "no_feasible_reuse": ScenarioExpectation(
        scenario=RecommendationScenario(
            scenario_id="no-feasible-reuse",
            forbid_material_reuse=True,
        ),
        expected_material_ids=(),
        expected_excluded_ids=("mat-site-a-tiles", "mat-site-b-tiles", "mat-site-e-tiles", "mat-site-g-wrong-size", "eq-site-h-unavailable"),
        expected_supplier_shortfall_units=500,
        expected_equipment_id="eq-site-d-cutter",
    ),
    "equipment_unavailable": ScenarioExpectation(
        scenario=RecommendationScenario(
            scenario_id="equipment-unavailable",
            force_equipment_unavailable_ids=("eq-site-d-cutter",),
        ),
        expected_material_ids=("mat-site-a-tiles", "mat-site-b-tiles"),
        expected_excluded_ids=("mat-site-e-tiles", "mat-site-g-wrong-size", "eq-site-d-cutter", "eq-site-h-unavailable"),
        expected_supplier_shortfall_units=70,
        expected_equipment_id="eq-commercial-fallback",
    ),
    "supplier_fallback_exact_total": ScenarioExpectation(
        scenario=RecommendationScenario(
            scenario_id="supplier-fallback-exact-total",
        ),
        expected_material_ids=("mat-site-a-tiles", "mat-site-b-tiles"),
        expected_excluded_ids=("mat-site-e-tiles", "mat-site-g-wrong-size", "eq-site-h-unavailable"),
        expected_supplier_shortfall_units=70,
        expected_equipment_id="eq-site-d-cutter",
    ),
}
