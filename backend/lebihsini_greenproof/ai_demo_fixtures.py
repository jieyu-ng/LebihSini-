from __future__ import annotations

from lebihsini_greenproof.contracts import InputSourceType, ResourceKind


VOICE_NOTE_BM = "Esok perlukan 500 tile kelabu 600 kali 600 dan mesin pemotong untuk dua hari."
ENGLISH_TYPED = "Need 500 grey porcelain tiles 600x600 and one tile cutter for two days by tomorrow 11:00."


MOCK_DEMAND_FIXTURES: dict[str, dict] = {
    "demo://voice-note/site-c/request-001": {
        "provider_language": "ms-MY",
        "fields": {
            "material_category": {"value": "porcelain_tile", "confidence": 0.92},
            "product_code": {"value": "PG-600-GREY", "confidence": 0.68},
            "colour": {"value": "grey", "confidence": 0.88},
            "dimensions": {"value": "600x600", "confidence": 0.93},
            "quantity_units": {"value": "500", "confidence": 0.90},
            "equipment_category": {"value": "tile_cutter", "confidence": 0.89},
            "equipment_duration_days": {"value": "2", "confidence": 0.86},
            "deadline_relative": {"value": "tomorrow", "confidence": 0.84},
        },
    },
    "demo://typed/en/request-001": {
        "provider_language": "en-MY",
        "fields": {
            "material_category": {"value": "porcelain_tile", "confidence": 0.96},
            "product_code": {"value": "PG-600-GREY", "confidence": 0.74},
            "colour": {"value": "grey", "confidence": 0.95},
            "dimensions": {"value": "600 x 600 mm", "confidence": 0.95},
            "quantity_units": {"value": 500, "confidence": 0.95},
            "equipment_category": {"value": "tile_cutter", "confidence": 0.93},
            "equipment_duration_days": {"value": 2, "confidence": 0.92},
            "deadline_relative": {"value": "tomorrow 11:00", "confidence": 0.90},
        },
    },
    "demo://handwritten/request-001": {
        "provider_language": "en-MY",
        "fields": {
            "material_category": {"value": "porcelain_tile", "confidence": 0.78},
            "product_code": {"value": None, "confidence": 0.20},
            "colour": {"value": "grey", "confidence": 0.72},
            "dimensions": {"value": "600x600", "confidence": 0.79},
            "quantity_units": {"value": "500", "confidence": 0.70},
            "equipment_category": {"value": "tile_cutter", "confidence": 0.77},
            "equipment_duration_days": {"value": "2", "confidence": 0.69},
            "deadline_relative": {"value": None, "confidence": 0.10},
        },
    },
    "demo://quotation/request-001": {
        "provider_language": "en-MY",
        "fields": {
            "material_category": {"value": "porcelain_tile", "confidence": 0.93},
            "product_code": {"value": "PG-600-GREY", "confidence": 0.91},
            "colour": {"value": "grey", "confidence": 0.88},
            "dimensions": {"value": "600x600", "confidence": 0.94},
            "quantity_units": {"value": 500, "confidence": 0.95},
            "equipment_category": {"value": "tile_cutter", "confidence": 0.61},
            "equipment_duration_days": {"value": 2, "confidence": 0.61},
            "deadline_relative": {"value": "tomorrow", "confidence": 0.83},
        },
    },
    "demo://whatsapp/request-001": {
        "provider_language": "ms-MY",
        "fields": {
            "material_category": {"value": "porcelain_tile", "confidence": 0.80},
            "product_code": {"value": None, "confidence": 0.15},
            "colour": {"value": "grey", "confidence": 0.82},
            "dimensions": {"value": "600 x 600", "confidence": 0.84},
            "quantity_units": {"value": "500", "confidence": 0.86},
            "equipment_category": {"value": "tile_cutter", "confidence": 0.79},
            "equipment_duration_days": {"value": "2", "confidence": 0.75},
            "deadline_relative": {"value": "tomorrow", "confidence": 0.80},
        },
    },
    "demo://low-confidence/request-001": {
        "provider_language": "unknown",
        "fields": {
            "material_category": {"value": None, "confidence": 0.10},
            "quantity_units": {"value": None, "confidence": 0.10},
            "deadline_relative": {"value": None, "confidence": 0.10},
        },
    },
}


MOCK_RESOURCE_FIXTURES: dict[str, dict] = {
    "demo://resource/site-a-photo-001": {
        "resource_kind": "material",
        "provider_language": "en-MY",
        "fields": {
            "material_category": {"value": "porcelain_tile", "confidence": 0.95},
            "brand": {"value": "DemoCeram", "confidence": 0.91},
            "product_code": {"value": "PG-600-GREY", "confidence": 0.94},
            "dimensions": {"value": "600x600", "confidence": 0.96},
            "colour": {"value": "grey", "confidence": 0.90},
            "batch_number": {"value": "BATCH-A1", "confidence": 0.76},
            "quantity_estimate_units": {"value": 300, "confidence": 0.88},
            "packaging_status": {"value": "sealed_boxes", "confidence": 0.93},
            "storage_condition": {"value": "indoor_dry", "confidence": 0.92},
            "available_from_at": {"value": "2026-06-20T08:00:00+08:00", "confidence": 0.90},
        },
    },
    "demo://resource/site-e-photo-001": {
        "resource_kind": "material",
        "provider_language": "en-MY",
        "fields": {
            "material_category": {"value": "porcelain_tile", "confidence": 0.55},
            "brand": {"value": None, "confidence": 0.15},
            "product_code": {"value": None, "confidence": 0.12},
            "dimensions": {"value": "600x600", "confidence": 0.51},
            "colour": {"value": "grey", "confidence": 0.58},
            "quantity_estimate_units": {"value": 100, "confidence": 0.61},
            "packaging_status": {"value": "loose_stacks", "confidence": 0.77},
            "storage_condition": {"value": "outdoor_exposed", "confidence": 0.94},
        },
    },
    "demo://resource/site-d-photo-001": {
        "resource_kind": "equipment",
        "provider_language": "en-MY",
        "fields": {
            "category": {"value": "tile_cutter", "confidence": 0.94},
            "brand_model": {"value": "Hilti DC-600 Demo", "confidence": 0.88},
            "capacity": {"value": "600mm", "confidence": 0.74},
            "maintenance_date_at": {"value": "2026-06-15T10:00:00+08:00", "confidence": 0.83},
            "maintenance_record_present": {"value": True, "confidence": 0.91},
            "operator_required": {"value": False, "confidence": 0.95},
            "visible_condition": {"value": "good", "confidence": 0.87},
        },
    },
}


PROMPT_FIXTURE_KEYS = {
    InputSourceType.VOICE_NOTE.value: "demand_extraction_v1",
    InputSourceType.RESOURCE_PHOTO.value: "resource_passport_extraction_v1",
}
