from __future__ import annotations

from dataclasses import dataclass

from lebihsini_greenproof.contracts import CarbonBreakdown, CostBreakdown


@dataclass(slots=True)
class FinancialInputs:
    new_material_cost_myr: float
    commercial_equipment_rental_myr: float
    supplier_delivery_cost_myr: float
    disposal_or_storage_cost_myr: float
    reuse_transfer_cost_myr: float
    new_material_shortfall_cost_myr: float
    reuse_transport_cost_myr: float
    equipment_cost_myr: float
    inspection_cost_myr: float
    additional_handling_cost_myr: float
    platform_fee_myr: float
    expected_delay_cost_myr: float


@dataclass(slots=True)
class CarbonInputs:
    material_carbon_factor_kgco2e_per_unit: float
    vehicle_factor_kgco2e_per_km: float
    quantity_units: int
    supplier_delivery_distance_km: float
    transfer_transport_distance_km: float
    number_of_trips: int
    processing_carbon_kgco2e: float
    new_material_shortfall_units: int
    disposal_or_storage_carbon_kgco2e: float


def calculate_cost_breakdown(inputs: FinancialInputs) -> CostBreakdown:
    normal_procurement_baseline = (
        inputs.new_material_cost_myr
        + inputs.commercial_equipment_rental_myr
        + inputs.supplier_delivery_cost_myr
        + inputs.disposal_or_storage_cost_myr
    )
    greenproof_total = (
        inputs.reuse_transfer_cost_myr
        + inputs.new_material_shortfall_cost_myr
        + inputs.reuse_transport_cost_myr
        + inputs.equipment_cost_myr
        + inputs.inspection_cost_myr
        + inputs.additional_handling_cost_myr
        + inputs.platform_fee_myr
        + inputs.expected_delay_cost_myr
    )
    reuse_material_and_equipment_cost = (
        inputs.reuse_transfer_cost_myr
        + inputs.new_material_shortfall_cost_myr
        + inputs.equipment_cost_myr
    )
    normal_material_and_equipment_cost = (
        inputs.new_material_cost_myr + inputs.commercial_equipment_rental_myr
    )
    gross_saving = normal_material_and_equipment_cost - reuse_material_and_equipment_cost
    net_saving = normal_procurement_baseline - greenproof_total
    return CostBreakdown(
        currency="MYR",
        new_material_cost_myr=inputs.new_material_cost_myr,
        commercial_equipment_rental_myr=inputs.commercial_equipment_rental_myr,
        supplier_delivery_cost_myr=inputs.supplier_delivery_cost_myr,
        disposal_or_storage_cost_myr=inputs.disposal_or_storage_cost_myr,
        reuse_transfer_cost_myr=inputs.reuse_transfer_cost_myr,
        new_material_shortfall_cost_myr=inputs.new_material_shortfall_cost_myr,
        reuse_transport_cost_myr=inputs.reuse_transport_cost_myr,
        equipment_cost_myr=inputs.equipment_cost_myr,
        inspection_cost_myr=inputs.inspection_cost_myr,
        additional_handling_cost_myr=inputs.additional_handling_cost_myr,
        platform_fee_myr=inputs.platform_fee_myr,
        expected_delay_cost_myr=inputs.expected_delay_cost_myr,
        normal_procurement_baseline_myr=normal_procurement_baseline,
        greenproof_total_myr=greenproof_total,
        gross_saving_myr=gross_saving,
        net_saving_myr=net_saving,
        working_capital_protected_myr=net_saving,
        assumptions=[
            "Transfer payments are treated as redistribution of existing value, not new system-wide value.",
            "All values are deterministic demo estimates in Malaysian ringgit.",
        ],
    )


def calculate_carbon_breakdown(inputs: CarbonInputs) -> CarbonBreakdown:
    baseline_carbon = (
        inputs.material_carbon_factor_kgco2e_per_unit * inputs.quantity_units
        + (inputs.supplier_delivery_distance_km * inputs.vehicle_factor_kgco2e_per_km)
        + inputs.disposal_or_storage_carbon_kgco2e
    )
    greenproof_carbon = (
        inputs.material_carbon_factor_kgco2e_per_unit * inputs.new_material_shortfall_units
        + (inputs.transfer_transport_distance_km * inputs.vehicle_factor_kgco2e_per_km * inputs.number_of_trips)
        + inputs.processing_carbon_kgco2e
    )
    return CarbonBreakdown(
        unit="kgCO2e",
        material_carbon_factor_kgco2e_per_unit=inputs.material_carbon_factor_kgco2e_per_unit,
        vehicle_factor_kgco2e_per_km=inputs.vehicle_factor_kgco2e_per_km,
        quantity_units=inputs.quantity_units,
        transport_distance_km=inputs.transfer_transport_distance_km,
        number_of_trips=inputs.number_of_trips,
        processing_carbon_kgco2e=inputs.processing_carbon_kgco2e,
        baseline_carbon_kgco2e=baseline_carbon,
        greenproof_carbon_kgco2e=greenproof_carbon,
        net_carbon_avoided_kgco2e=baseline_carbon - greenproof_carbon,
        assumptions=[
            "Transport carbon is estimated from distance x vehicle factor x trip count.",
            "All carbon values are estimates using fictional demo assumptions.",
        ],
    )
