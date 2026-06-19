"""Reference scenario scaffold for validating contracts and demo assumptions.

This module is intentionally limited. It is not the final optimiser, not the
production recommendation engine, and not the source of truth for future
ranking strategy. Its purpose is to validate shared contracts, prepared demo
data, and scenario expectations before Person 4 implements the real composer.
"""

from __future__ import annotations

from dataclasses import dataclass

from lebihsini_greenproof.contracts import (
    CALCULATION_VERSION,
    CarbonBreakdown,
    CostBreakdown,
    ExcludedResource,
    RecommendationOutput,
    ResourceCandidate,
    ResourceKind,
    RiskCategory,
    SelectedEquipment,
    SelectedMaterialResource,
    Verdict,
)
from lebihsini_greenproof.demo_data import DemoDataset
from lebihsini_greenproof.explanations import EXPLANATION_TEXT
from lebihsini_greenproof.formulas import (
    CarbonInputs,
    FinancialInputs,
    calculate_carbon_breakdown,
    calculate_cost_breakdown,
)


@dataclass(slots=True)
class ScenarioConfig:
    scenario_id: str
    lead_time_limit_minutes: int
    equipment_required: bool = True
    allow_reuse_when_net_carbon_negative: bool = False
    force_equipment_unavailable_ids: tuple[str, ...] = ()
    forbid_material_reuse: bool = False


def _risk_value(risk: RiskCategory) -> int:
    return {
        RiskCategory.GREEN: 1,
        RiskCategory.AMBER: 2,
        RiskCategory.RED: 3,
    }[risk]


def evaluate_material_candidates(dataset: DemoDataset, scenario: ScenarioConfig) -> tuple[list[ResourceCandidate], list[ExcludedResource]]:
    """Apply a small set of deterministic eligibility checks for fixture validation.

    This is intentionally not a complete constraint engine. It only supports the
    prepared scenario tests that protect the contract layer.
    """
    demand = dataset.demand
    eligible: list[ResourceCandidate] = []
    excluded: list[ExcludedResource] = []
    for resource in dataset.material_resources:
        reasons: list[str] = []
        conditions: list[str] = []
        if scenario.forbid_material_reuse:
            reasons.append(EXPLANATION_TEXT["normal_procurement_recommended"])
        if resource.category != demand.material_category:
            reasons.append("Material category is incompatible with the request.")
        if resource.product_code != demand.product_code:
            reasons.append("Product specification is incompatible with the request.")
        if (
            resource.dimension_mm_width != demand.dimension_mm_width
            or resource.dimension_mm_height != demand.dimension_mm_height
        ):
            reasons.append("Dimensions do not match the request.")
        if resource.quantity_units <= 0:
            reasons.append("Available quantity is zero.")
        if resource.distance_to_site_km > demand.maximum_distance_km:
            reasons.append("Resource exceeds the maximum allowed distance.")
        if _risk_value(resource.risk_category) > _risk_value(demand.maximum_risk):
            reasons.append("Risk exceeds the allowed tolerance.")
        if not resource.has_required_documentation:
            reasons.append(EXPLANATION_TEXT["documentation_missing"])
        if resource.travel_time_to_site_minutes > scenario.lead_time_limit_minutes:
            reasons.append(EXPLANATION_TEXT["deadline_infeasible"])
        if resource.site_id == "site-e":
            reasons.append(EXPLANATION_TEXT["site_e_uncertainty"])
        if resource.inspection_required and resource.risk_category == RiskCategory.AMBER:
            conditions.append(EXPLANATION_TEXT["inspection_required"])

        if reasons:
            excluded.append(
                ExcludedResource(
                    resource_id=resource.resource_id,
                    site_id=resource.site_id,
                    site_name=resource.site_name,
                    reason_code="material_ineligible",
                    reason_text=" ".join(dict.fromkeys(reasons)),
                    confidence=resource.confidence,
                )
            )
            continue

        eligible.append(
            ResourceCandidate(
                resource_id=resource.resource_id,
                resource_kind=ResourceKind.MATERIAL,
                eligible=True,
                available_quantity_units=resource.quantity_units,
                confidence=resource.confidence,
                risk_category=resource.risk_category,
                rank_score=(resource.confidence * 100.0) - resource.distance_to_site_km - (_risk_value(resource.risk_category) * 10.0),
                conditions=conditions,
                reasons=[EXPLANATION_TEXT["resource_selected"]],
            )
        )
    return eligible, excluded


def evaluate_equipment(dataset: DemoDataset, scenario: ScenarioConfig) -> tuple[SelectedEquipment | None, list[ExcludedResource]]:
    """Select one equipment candidate for scenario validation.

    This function is placeholder logic and must not be treated as the final
    equipment optimiser.
    """
    demand = dataset.demand
    excluded: list[ExcludedResource] = []
    selected: SelectedEquipment | None = None
    if not scenario.equipment_required:
        return None, excluded
    for equipment in dataset.equipment_resources:
        reasons: list[str] = []
        if equipment.resource_id in scenario.force_equipment_unavailable_ids:
            reasons.append("Equipment was forced unavailable by the scenario fixture.")
        if equipment.category != demand.equipment_category:
            reasons.append("Equipment category is incompatible with the request.")
        if equipment.travel_time_to_site_minutes > scenario.lead_time_limit_minutes:
            reasons.append(EXPLANATION_TEXT["deadline_infeasible"])
        if not equipment.maintenance_record_present or equipment.maintenance_confidence < 0.8:
            reasons.append("Maintenance evidence does not meet the minimum threshold.")
        if reasons:
            excluded.append(
                ExcludedResource(
                    resource_id=equipment.resource_id,
                    site_id=equipment.site_id,
                    site_name=equipment.site_name,
                    reason_code="equipment_ineligible",
                    reason_text=" ".join(dict.fromkeys(reasons)),
                    confidence=equipment.maintenance_confidence,
                )
            )
            continue
        if selected is None:
            selected = SelectedEquipment(
                resource_id=equipment.resource_id,
                site_id=equipment.site_id,
                site_name=equipment.site_name,
                category=equipment.category,
                duration_days=demand.equipment_duration_days,
                rental_cost_myr=equipment.rental_rate_myr_per_day * demand.equipment_duration_days,
                conditions=[],
            )
    return selected, excluded


def build_reference_recommendation(dataset: DemoDataset, scenario: ScenarioConfig) -> RecommendationOutput:
    """Build a reference recommendation payload for tests and JSON examples.

    Warning:
    - This is a validation scaffold, not the final optimiser.
    - Placeholder ranking and selection behaviour may change once the real
      `constraints.py` and `composer.py` modules exist.
    - Use this to validate shared payloads and demo assumptions only.
    """
    eligible_materials, excluded_materials = evaluate_material_candidates(dataset, scenario)
    selected_materials: list[SelectedMaterialResource] = []
    eligible_by_id = {candidate.resource_id: candidate for candidate in eligible_materials}
    quantity_remaining = dataset.demand.quantity_units
    selected_transport_distance = 0.0
    amber_count = 0

    for resource in sorted(
        dataset.material_resources,
        key=lambda item: (
            _risk_value(item.risk_category),
            item.travel_time_to_site_minutes,
            item.transfer_price_myr_per_unit,
        ),
    ):
        if quantity_remaining <= 0:
            break
        if resource.resource_id not in eligible_by_id:
            continue
        taken = min(resource.quantity_units, quantity_remaining)
        quantity_remaining -= taken
        selected_transport_distance += resource.distance_to_site_km
        if resource.risk_category == RiskCategory.AMBER:
            amber_count += 1
        selected_materials.append(
            SelectedMaterialResource(
                resource_id=resource.resource_id,
                site_id=resource.site_id,
                site_name=resource.site_name,
                quantity_units=taken,
                transfer_price_myr_per_unit=resource.transfer_price_myr_per_unit,
                distance_km=resource.distance_to_site_km,
                inspection_required=resource.inspection_required,
                conditions=[EXPLANATION_TEXT["inspection_required"]] if resource.inspection_required else [],
            )
        )

    selected_equipment, excluded_equipment = evaluate_equipment(dataset, scenario)
    excluded_resources = excluded_materials + excluded_equipment

    reuse_transfer_cost = sum(
        item.quantity_units * item.transfer_price_myr_per_unit for item in selected_materials
    )
    reuse_transport_cost = selected_transport_distance * 4.0
    new_material_shortfall_cost = quantity_remaining * dataset.supplier_unit_price_myr
    equipment_cost = selected_equipment.rental_cost_myr if selected_equipment else 0.0
    commercial_equipment_rental = (
        dataset.commercial_equipment_rental_daily_myr * dataset.demand.equipment_duration_days
    )
    inspection_cost = amber_count * dataset.inspection_cost_per_amber_resource_myr
    cost_breakdown = calculate_cost_breakdown(
        FinancialInputs(
            new_material_cost_myr=dataset.demand.quantity_units * dataset.supplier_unit_price_myr,
            commercial_equipment_rental_myr=commercial_equipment_rental,
            supplier_delivery_cost_myr=dataset.supplier_delivery_cost_myr,
            disposal_or_storage_cost_myr=dataset.disposal_or_storage_cost_myr,
            reuse_transfer_cost_myr=reuse_transfer_cost,
            new_material_shortfall_cost_myr=new_material_shortfall_cost,
            reuse_transport_cost_myr=reuse_transport_cost,
            equipment_cost_myr=equipment_cost,
            inspection_cost_myr=inspection_cost,
            additional_handling_cost_myr=dataset.additional_handling_cost_myr,
            platform_fee_myr=dataset.platform_fee_myr,
            expected_delay_cost_myr=dataset.expected_delay_cost_myr,
        )
    )
    carbon_breakdown = calculate_carbon_breakdown(
        CarbonInputs(
            material_carbon_factor_kgco2e_per_unit=1.8,
            vehicle_factor_kgco2e_per_km=0.27,
            quantity_units=dataset.demand.quantity_units,
            supplier_delivery_distance_km=dataset.supplier_delivery_distance_km,
            transfer_transport_distance_km=selected_transport_distance,
            number_of_trips=max(1, len(selected_materials)),
            processing_carbon_kgco2e=5.0,
            new_material_shortfall_units=quantity_remaining,
            disposal_or_storage_carbon_kgco2e=dataset.disposal_or_storage_carbon_kgco2e,
        )
    )

    if selected_materials and quantity_remaining > 0:
        verdict = Verdict.PARTIAL_REUSE_RECOMMENDED
        reasons = [
            EXPLANATION_TEXT["partial_reuse_recommended"],
            EXPLANATION_TEXT["supplier_fallback_required"],
        ]
    elif selected_materials:
        verdict = Verdict.GREENPROOF_RECOMMENDED
        reasons = [EXPLANATION_TEXT["resource_selected"]]
    else:
        verdict = Verdict.NORMAL_PROCUREMENT_RECOMMENDED
        reasons = [EXPLANATION_TEXT["normal_procurement_recommended"]]

    if not scenario.allow_reuse_when_net_carbon_negative and carbon_breakdown.net_carbon_avoided_kgco2e < 0:
        verdict = Verdict.NORMAL_PROCUREMENT_RECOMMENDED
        reasons = [EXPLANATION_TEXT["negative_net_carbon_benefit"]]
        selected_materials = []
        quantity_remaining = dataset.demand.quantity_units

    conditions = []
    if amber_count:
        conditions.append(EXPLANATION_TEXT["inspection_required"])
    if quantity_remaining > 0:
        conditions.append(EXPLANATION_TEXT["supplier_fallback_required"])

    return RecommendationOutput(
        recommendation_id=f"rec-{scenario.scenario_id}",
        verdict=verdict,
        deadline_met=True,
        selected_material_resources=selected_materials,
        selected_equipment=selected_equipment,
        excluded_resources=excluded_resources,
        supplier_shortfall_units=quantity_remaining,
        quantity_fulfilled_units=sum(item.quantity_units for item in selected_materials) + quantity_remaining,
        cost_breakdown=cost_breakdown,
        carbon_breakdown=carbon_breakdown,
        conditions=conditions,
        reasons=reasons,
        assumptions=[
            EXPLANATION_TEXT["estimated_assumptions"],
            "This reference flow is a foundation validator, not the final optimiser.",
        ],
        confidence=0.89,
        calculation_version=CALCULATION_VERSION,
    )
