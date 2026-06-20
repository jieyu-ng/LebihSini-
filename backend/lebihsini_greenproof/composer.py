from __future__ import annotations

from dataclasses import dataclass

from lebihsini_greenproof.constraints import MaterialCandidateEvaluation, evaluate_material_candidate
from lebihsini_greenproof.contracts import (
    CALCULATION_VERSION,
    DemandRequest,
    ExcludedResource,
    RecommendationOutput,
    SelectedMaterialResource,
    Verdict,
)
from lebihsini_greenproof.demo_data import DemoDataset
from lebihsini_greenproof.equipment import select_equipment
from lebihsini_greenproof.explanations import EXPLANATION_TEXT
from lebihsini_greenproof.formulas import (
    CarbonInputs,
    FinancialInputs,
    calculate_carbon_breakdown,
    calculate_cost_breakdown,
)
from lebihsini_greenproof.ranking import rank_material_candidates
from lebihsini_greenproof.urgency import RecommendationScenario, resolve_deadline_at, revise_demand_deadline


@dataclass(slots=True)
class MaterialCompositionResult:
    selected_resources: list[SelectedMaterialResource]
    supplier_shortfall_units: int
    excluded_resources: list[ExcludedResource]
    selected_evaluations: list[MaterialCandidateEvaluation]


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def compose_material_plan(
    dataset: DemoDataset,
    demand: DemandRequest,
    scenario: RecommendationScenario | None = None,
) -> MaterialCompositionResult:
    deadline_at = resolve_deadline_at(demand, scenario)
    evaluations = [
        evaluate_material_candidate(
            demand,
            resource,
            deadline_at,
            dataset.material_collection_buffer_minutes,
            forbid_material_reuse=scenario.forbid_material_reuse if scenario else False,
        )
        for resource in dataset.material_resources
    ]
    ranked = rank_material_candidates(evaluations)
    remaining = demand.quantity_units
    selected_resources: list[SelectedMaterialResource] = []
    selected_evaluations: list[MaterialCandidateEvaluation] = []
    for evaluation in ranked:
        if remaining <= 0:
            break
        allocated = min(evaluation.resource.quantity_units, remaining)
        if allocated <= 0:
            continue
        remaining -= allocated
        selected_evaluations.append(evaluation)
        selected_resources.append(
            SelectedMaterialResource(
                resource_id=evaluation.resource.resource_id,
                site_id=evaluation.resource.site_id,
                site_name=evaluation.resource.site_name,
                quantity_units=allocated,
                transfer_price_myr_per_unit=evaluation.resource.transfer_price_myr_per_unit,
                distance_km=evaluation.resource.distance_to_site_km,
                inspection_required=evaluation.resource.inspection_required,
                conditions=_dedupe(evaluation.conditions),
            )
        )

    excluded_resources = [item.exclusion for item in evaluations if item.exclusion is not None]
    return MaterialCompositionResult(
        selected_resources=selected_resources,
        supplier_shortfall_units=max(0, remaining),
        excluded_resources=excluded_resources,
        selected_evaluations=selected_evaluations,
    )


def _build_reasons(
    baseline_deadline_at: str,
    demand: DemandRequest,
    scenario: RecommendationScenario | None,
    selected_resources: list[SelectedMaterialResource],
    supplier_shortfall_units: int,
    net_saving_myr: float,
    net_carbon_avoided_kgco2e: float,
) -> list[str]:
    reasons: list[str] = []
    if scenario and scenario.revised_deadline_at and scenario.revised_deadline_at != baseline_deadline_at:
        reasons.append(EXPLANATION_TEXT["urgency_plan_changed"])
    if selected_resources and supplier_shortfall_units == 0:
        reasons.append(EXPLANATION_TEXT["resource_selected"])
    elif selected_resources:
        reasons.append(EXPLANATION_TEXT["partial_reuse_recommended"])
    else:
        reasons.append(EXPLANATION_TEXT["normal_procurement_recommended"])
    if supplier_shortfall_units > 0:
        reasons.append(EXPLANATION_TEXT["supplier_selected"])
    reasons.append(
        "Estimated total cost remains lower than normal procurement."
        if net_saving_myr >= 0
        else "Estimated total cost is higher than normal procurement under the stated assumptions."
    )
    reasons.append(
        "Estimated carbon remains lower than normal procurement after transport."
        if net_carbon_avoided_kgco2e >= 0
        else "Estimated transport and processing impact reduce or remove the carbon benefit."
    )
    reasons.append(EXPLANATION_TEXT["deadline_feasible"])
    return _dedupe(reasons)


def _calculate_plan_confidence(
    demand: DemandRequest,
    selected_resources: list[SelectedMaterialResource],
    selected_evaluations: list[MaterialCandidateEvaluation],
    selected_equipment_confidence: float,
) -> float:
    if not selected_resources:
        return round(max(0.0, min(1.0, demand.extraction_confidence * 0.95)), 2)
    weighted_sum = demand.extraction_confidence
    count = 1
    for evaluation in selected_evaluations:
        weighted_sum += evaluation.resource.confidence
        count += 1
    if selected_equipment_confidence > 0:
        weighted_sum += selected_equipment_confidence
        count += 1
    return round(max(0.0, min(1.0, weighted_sum / count)), 2)


def generate_recommendation(
    dataset: DemoDataset,
    demand: DemandRequest | None = None,
    scenario: RecommendationScenario | None = None,
) -> RecommendationOutput:
    base_demand = demand or dataset.demand
    resolved_deadline = resolve_deadline_at(base_demand, scenario)
    confirmed_demand = (
        revise_demand_deadline(base_demand, resolved_deadline.isoformat())
        if scenario and scenario.revised_deadline_at
        else base_demand
    )
    material_result = compose_material_plan(dataset, confirmed_demand, scenario)
    selected_equipment, equipment_excluded, selected_equipment_total_cost = select_equipment(
        confirmed_demand,
        dataset.equipment_resources,
        dataset.commercial_equipment_fallback,
        resolved_deadline,
        dataset.equipment_collection_buffer_minutes,
        dataset.equipment_return_buffer_minutes,
        force_unavailable_ids=scenario.force_equipment_unavailable_ids if scenario else (),
    )

    selected_total = sum(item.quantity_units for item in material_result.selected_resources)
    supplier_shortfall_units = material_result.supplier_shortfall_units
    quantity_fulfilled_units = selected_total + supplier_shortfall_units
    reuse_transfer_cost = sum(
        item.quantity_units * item.transfer_price_myr_per_unit
        for item in material_result.selected_resources
    )
    reuse_transport_cost = sum(
        evaluation.resource.distance_to_site_km * evaluation.resource.transport_rate_myr_per_km
        for evaluation in material_result.selected_evaluations
    )
    inspection_cost = sum(
        dataset.inspection_cost_per_amber_resource_myr
        for evaluation in material_result.selected_evaluations
        if evaluation.resource.inspection_required or evaluation.resource.risk_category.value == "amber"
    )
    new_material_shortfall_cost = supplier_shortfall_units * dataset.supplier_unit_price_myr
    commercial_equipment_rental_myr = dataset.commercial_equipment_rental_daily_myr * confirmed_demand.equipment_duration_days

    cost_breakdown = calculate_cost_breakdown(
        FinancialInputs(
            new_material_cost_myr=confirmed_demand.quantity_units * dataset.supplier_unit_price_myr,
            commercial_equipment_rental_myr=commercial_equipment_rental_myr,
            supplier_delivery_cost_myr=dataset.supplier_delivery_cost_myr,
            disposal_or_storage_cost_myr=dataset.disposal_or_storage_cost_myr,
            reuse_transfer_cost_myr=reuse_transfer_cost,
            new_material_shortfall_cost_myr=new_material_shortfall_cost,
            reuse_transport_cost_myr=reuse_transport_cost,
            equipment_cost_myr=selected_equipment_total_cost,
            inspection_cost_myr=inspection_cost,
            additional_handling_cost_myr=dataset.additional_handling_cost_myr,
            platform_fee_myr=dataset.platform_fee_myr,
            expected_delay_cost_myr=dataset.expected_delay_cost_myr,
        )
    )
    carbon_breakdown = calculate_carbon_breakdown(
        CarbonInputs(
            material_carbon_factor_kgco2e_per_unit=1.8,
            vehicle_factor_kgco2e_per_km=dataset.supplier_vehicle_factor_kgco2e_per_km,
            quantity_units=confirmed_demand.quantity_units,
            supplier_delivery_distance_km=dataset.supplier_delivery_distance_km,
            transfer_transport_distance_km=sum(item.distance_km for item in material_result.selected_resources),
            number_of_trips=max(1, len(material_result.selected_resources)) if material_result.selected_resources else 1,
            processing_carbon_kgco2e=dataset.reuse_processing_carbon_kgco2e,
            new_material_shortfall_units=supplier_shortfall_units,
            disposal_or_storage_carbon_kgco2e=dataset.disposal_or_storage_carbon_kgco2e,
        )
    )

    excluded_resources = [*material_result.excluded_resources, *equipment_excluded]
    if (
        material_result.selected_resources
        and not (scenario.allow_reuse_when_net_carbon_negative if scenario else False)
        and carbon_breakdown.net_carbon_avoided_kgco2e < 0
    ):
        excluded_resources.extend(
            ExcludedResource(
                resource_id=item.resource_id,
                site_id=item.site_id,
                site_name=item.site_name,
                reason_code="negative_net_carbon_benefit",
                reason_text=EXPLANATION_TEXT["negative_net_carbon_benefit"],
                confidence=1.0,
                evidence_notes=[],
            )
            for item in material_result.selected_resources
        )
        material_result = MaterialCompositionResult(
            selected_resources=[],
            supplier_shortfall_units=confirmed_demand.quantity_units,
            excluded_resources=material_result.excluded_resources,
            selected_evaluations=[],
        )
        selected_total = 0
        supplier_shortfall_units = confirmed_demand.quantity_units
        quantity_fulfilled_units = confirmed_demand.quantity_units
        cost_breakdown = calculate_cost_breakdown(
            FinancialInputs(
                new_material_cost_myr=confirmed_demand.quantity_units * dataset.supplier_unit_price_myr,
                commercial_equipment_rental_myr=commercial_equipment_rental_myr,
                supplier_delivery_cost_myr=dataset.supplier_delivery_cost_myr,
                disposal_or_storage_cost_myr=dataset.disposal_or_storage_cost_myr,
                reuse_transfer_cost_myr=0.0,
                new_material_shortfall_cost_myr=confirmed_demand.quantity_units * dataset.supplier_unit_price_myr,
                reuse_transport_cost_myr=0.0,
                equipment_cost_myr=selected_equipment_total_cost,
                inspection_cost_myr=0.0,
                additional_handling_cost_myr=0.0,
                platform_fee_myr=dataset.platform_fee_myr,
                expected_delay_cost_myr=dataset.expected_delay_cost_myr,
            )
        )
        carbon_breakdown = calculate_carbon_breakdown(
            CarbonInputs(
                material_carbon_factor_kgco2e_per_unit=1.8,
                vehicle_factor_kgco2e_per_km=dataset.supplier_vehicle_factor_kgco2e_per_km,
                quantity_units=confirmed_demand.quantity_units,
                supplier_delivery_distance_km=dataset.supplier_delivery_distance_km,
                transfer_transport_distance_km=0.0,
                number_of_trips=1,
                processing_carbon_kgco2e=0.0,
                new_material_shortfall_units=confirmed_demand.quantity_units,
                disposal_or_storage_carbon_kgco2e=dataset.disposal_or_storage_carbon_kgco2e,
            )
        )

    conditions = _dedupe(
        [
            condition
            for item in material_result.selected_resources
            for condition in item.conditions
        ]
        + (selected_equipment.conditions if selected_equipment else [])
        + ([EXPLANATION_TEXT["supplier_fallback_required"]] if supplier_shortfall_units > 0 else [])
    )
    if selected_total == confirmed_demand.quantity_units:
        verdict = Verdict.GREENPROOF_RECOMMENDED
    elif selected_total > 0 and quantity_fulfilled_units == confirmed_demand.quantity_units:
        verdict = Verdict.PARTIAL_REUSE_RECOMMENDED
    elif quantity_fulfilled_units == confirmed_demand.quantity_units:
        verdict = Verdict.NORMAL_PROCUREMENT_RECOMMENDED
    else:
        verdict = Verdict.MANUAL_REVIEW_REQUIRED

    selected_equipment_confidence = 0.0
    if selected_equipment:
        if selected_equipment.resource_id == dataset.commercial_equipment_fallback.resource_id:
            selected_equipment_confidence = dataset.commercial_equipment_fallback.maintenance_confidence
        else:
            match = next(
                item for item in dataset.equipment_resources if item.resource_id == selected_equipment.resource_id
            )
            selected_equipment_confidence = match.maintenance_confidence

    reasons = _build_reasons(
        dataset.demand.deadline_at,
        confirmed_demand,
        scenario,
        material_result.selected_resources,
        supplier_shortfall_units,
        cost_breakdown.net_saving_myr,
        carbon_breakdown.net_carbon_avoided_kgco2e,
    )

    return RecommendationOutput(
        recommendation_id=f"rec-{scenario.scenario_id if scenario else 'default'}",
        verdict=verdict,
        deadline_met=quantity_fulfilled_units == confirmed_demand.quantity_units and selected_equipment is not None,
        selected_material_resources=material_result.selected_resources,
        selected_equipment=selected_equipment,
        excluded_resources=excluded_resources,
        supplier_shortfall_units=supplier_shortfall_units,
        quantity_fulfilled_units=quantity_fulfilled_units,
        cost_breakdown=cost_breakdown,
        carbon_breakdown=carbon_breakdown,
        conditions=conditions,
        reasons=reasons,
        assumptions=[
            EXPLANATION_TEXT["estimated_assumptions"],
            "Deadline feasibility uses deterministic precomputed travel times plus simple collection buffers.",
            "Supplier F is treated as a structured fallback with prepared delivery assumptions.",
        ],
        confidence=_calculate_plan_confidence(
            confirmed_demand,
            material_result.selected_resources,
            material_result.selected_evaluations,
            selected_equipment_confidence,
        ),
        calculation_version=CALCULATION_VERSION,
    )
