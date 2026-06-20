import unittest


class CompatibilityTests(unittest.TestCase):
    def test_financial_module_reexports_existing_formula_api(self) -> None:
        from lebihsini_greenproof.financial import FinancialInputs, calculate_cost_breakdown

        result = calculate_cost_breakdown(
            FinancialInputs(
                new_material_cost_myr=10.0,
                commercial_equipment_rental_myr=5.0,
                supplier_delivery_cost_myr=2.0,
                disposal_or_storage_cost_myr=1.0,
                reuse_transfer_cost_myr=4.0,
                new_material_shortfall_cost_myr=3.0,
                reuse_transport_cost_myr=1.0,
                equipment_cost_myr=2.0,
                inspection_cost_myr=1.0,
                additional_handling_cost_myr=1.0,
                platform_fee_myr=1.0,
                expected_delay_cost_myr=0.0,
            )
        )
        self.assertEqual(result.currency, "MYR")

    def test_carbon_module_reexports_existing_formula_api(self) -> None:
        from lebihsini_greenproof.carbon import CarbonInputs, calculate_carbon_breakdown

        result = calculate_carbon_breakdown(
            CarbonInputs(
                material_carbon_factor_kgco2e_per_unit=1.0,
                vehicle_factor_kgco2e_per_km=0.5,
                quantity_units=10,
                supplier_delivery_distance_km=5.0,
                transfer_transport_distance_km=2.0,
                number_of_trips=1,
                processing_carbon_kgco2e=1.0,
                new_material_shortfall_units=4,
                disposal_or_storage_carbon_kgco2e=1.0,
            )
        )
        self.assertEqual(result.unit, "kgCO2e")

    def test_explanation_module_available(self) -> None:
        from lebihsini_greenproof.explanation import build_selection_reason

        self.assertTrue(build_selection_reason(1, 0))


if __name__ == "__main__":
    unittest.main()
