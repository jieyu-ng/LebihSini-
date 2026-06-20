import unittest

from lebihsini_greenproof.confidence import (
    confidence_label,
    has_low_confidence_critical_field,
    identify_missing_critical_fields,
)
from lebihsini_greenproof.contracts import ConfidenceLabel, ExtractedField


class ConfidencePolicyTests(unittest.TestCase):
    def test_high_medium_low_thresholds(self) -> None:
        self.assertEqual(confidence_label(0.90), ConfidenceLabel.HIGH)
        self.assertEqual(confidence_label(0.70), ConfidenceLabel.MEDIUM)
        self.assertEqual(confidence_label(0.20), ConfidenceLabel.LOW)

    def test_invalid_confidence_values(self) -> None:
        with self.assertRaises(ValueError):
            confidence_label(1.2)

    def test_low_confidence_critical_field_detected(self) -> None:
        fields = [
            ExtractedField(
                field_name="quantity_units",
                extracted_value=500,
                confidence_score=0.40,
                confidence_label=ConfidenceLabel.LOW,
                evidence_reference=None,
                confirmation_required=True,
            )
        ]
        self.assertTrue(has_low_confidence_critical_field(fields))

    def test_missing_critical_field_detected(self) -> None:
        missing = identify_missing_critical_fields(
            {
                "material_category": "porcelain_tile",
                "product_code": None,
                "dimension_mm_width": 600,
                "dimension_mm_height": 600,
                "quantity_units": 500,
                "deadline_at": None,
                "equipment_category": "tile_cutter",
            }
        )
        self.assertEqual({item.field_name for item in missing}, {"deadline_at", "product_code"})


if __name__ == "__main__":
    unittest.main()
