from __future__ import annotations

from dataclasses import dataclass

from lebihsini_greenproof.foundation import ScenarioConfig


@dataclass(slots=True)
class ScenarioExpectation:
    scenario: ScenarioConfig
    expected_material_ids: tuple[str, ...]
    expected_excluded_ids: tuple[str, ...]
    expected_supplier_shortfall_units: int
    expected_equipment_id: str | None


SCENARIO_FIXTURES = {
    "tomorrow_deadline": ScenarioExpectation(
        scenario=ScenarioConfig(
            scenario_id="tomorrow-deadline",
            lead_time_limit_minutes=60,
        ),
        expected_material_ids=("mat-site-a-tiles", "mat-site-b-tiles"),
        expected_excluded_ids=("mat-site-e-tiles", "mat-site-g-wrong-size", "eq-site-h-unavailable"),
        expected_supplier_shortfall_units=70,
        expected_equipment_id="eq-site-d-cutter",
    ),
    "three_hour_deadline": ScenarioExpectation(
        scenario=ScenarioConfig(
            scenario_id="three-hour-deadline",
            lead_time_limit_minutes=45,
        ),
        expected_material_ids=("mat-site-a-tiles",),
        expected_excluded_ids=("mat-site-b-tiles", "mat-site-e-tiles", "mat-site-g-wrong-size", "eq-site-h-unavailable"),
        expected_supplier_shortfall_units=200,
        expected_equipment_id="eq-site-d-cutter",
    ),
    "site_e_unreadable": ScenarioExpectation(
        scenario=ScenarioConfig(
            scenario_id="site-e-unreadable",
            lead_time_limit_minutes=60,
        ),
        expected_material_ids=("mat-site-a-tiles", "mat-site-b-tiles"),
        expected_excluded_ids=("mat-site-e-tiles", "mat-site-g-wrong-size", "eq-site-h-unavailable"),
        expected_supplier_shortfall_units=70,
        expected_equipment_id="eq-site-d-cutter",
    ),
    "no_feasible_reuse": ScenarioExpectation(
        scenario=ScenarioConfig(
            scenario_id="no-feasible-reuse",
            lead_time_limit_minutes=60,
            forbid_material_reuse=True,
        ),
        expected_material_ids=(),
        expected_excluded_ids=("mat-site-a-tiles", "mat-site-b-tiles", "mat-site-e-tiles", "mat-site-g-wrong-size", "eq-site-h-unavailable"),
        expected_supplier_shortfall_units=500,
        expected_equipment_id="eq-site-d-cutter",
    ),
    "equipment_unavailable": ScenarioExpectation(
        scenario=ScenarioConfig(
            scenario_id="equipment-unavailable",
            lead_time_limit_minutes=60,
            force_equipment_unavailable_ids=("eq-site-d-cutter",),
        ),
        expected_material_ids=("mat-site-a-tiles", "mat-site-b-tiles"),
        expected_excluded_ids=("mat-site-e-tiles", "mat-site-g-wrong-size", "eq-site-d-cutter", "eq-site-h-unavailable"),
        expected_supplier_shortfall_units=70,
        expected_equipment_id=None,
    ),
    "supplier_fallback_exact_total": ScenarioExpectation(
        scenario=ScenarioConfig(
            scenario_id="supplier-fallback-exact-total",
            lead_time_limit_minutes=60,
        ),
        expected_material_ids=("mat-site-a-tiles", "mat-site-b-tiles"),
        expected_excluded_ids=("mat-site-e-tiles", "mat-site-g-wrong-size", "eq-site-h-unavailable"),
        expected_supplier_shortfall_units=70,
        expected_equipment_id="eq-site-d-cutter",
    ),
}
