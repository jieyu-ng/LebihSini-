# LebihSini GreenProof API Contract

All request and response shapes below use canonical `snake_case` and are documented for MVP frontend/backend alignment. FastAPI routes are not implemented in this repository yet.

Units:

- quantity: units
- dimensions: millimetres
- distance: kilometres
- travel time: minutes
- money: Malaysian ringgit
- carbon: kgCO2e
- confidence: decimal between 0.0 and 1.0
- datetime: ISO 8601

## Common Error Shape

```json
{
  "error": {
    "code": "MISSING_CRITICAL_FIELD",
    "message": "Critical field `deadline_at` is missing and must be confirmed before submission.",
    "details": {}
  }
}
```

Standard codes:

- `INPUT_UNREADABLE`
- `UNSUPPORTED_INPUT_TYPE`
- `MISSING_CRITICAL_FIELD`
- `LOW_CONFIDENCE_CONFIRMATION_REQUIRED`
- `AI_PROVIDER_UNAVAILABLE`
- `INVALID_PROVIDER_OUTPUT`
- `MANUAL_INSPECTION_REQUIRED`
- `DEADLINE_INFEASIBLE`

## POST /api/extract-request

Purpose: send one raw input through the AI extraction boundary.

Status: future contract only

Request body:

```json
{
  "request_id": "extract-bm-001",
  "source_type": "voice_note",
  "content": "Esok perlukan 500 tile kelabu 600 kali 600 dan mesin pemotong untuk dua hari.",
  "content_reference": "demo://voice-note/site-c/request-001",
  "input_language": "ms-MY",
  "reference_datetime": "2026-06-20T09:00:00+08:00",
  "timezone": "Asia/Kuala_Lumpur"
}
```

Response body:

Use [examples/bahasa_voice_extraction.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/bahasa_voice_extraction.json) as the canonical example.

Required fields:

- `request_id`
- `source_type`
- `detected_language`
- `extracted_fields`
- `missing_fields`
- `warnings`
- `model_metadata`
- `can_proceed_to_confirmation`
- `requires_manual_review`
- `normalized_demand`

## POST /api/extract-request/confirm

Purpose: convert a structured extraction into confirmed values after user review.

Status: future contract only

Request body:

```json
{
  "request_id": "extract-bm-001",
  "action": "accept",
  "confirmed_values": {
    "product_code": "PG-600-GREY"
  },
  "confirmed_at": "2026-06-20T09:05:00+08:00"
}
```

Response body:

Use [examples/confirmed_demand.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/confirmed_demand.json) as the canonical example.

Notes:

- confirmed values become the system of record
- raw provider values must not go directly into the optimiser
- missing critical fields must block confirmed demand creation

## POST /api/recommendations

Purpose: generate a recommendation from a confirmed demand request.

Status: future contract only

Request body:

```json
{
  "demand": {
    "demand_id": "demand-confirmed-extract-bm-001",
    "requesting_site_id": "site-c",
    "material_category": "porcelain_tile",
    "product_code": "PG-600-GREY",
    "colour": "grey",
    "dimension_mm_width": 600,
    "dimension_mm_height": 600,
    "quantity_units": 500,
    "deadline_at": "2026-06-21T11:00:00+08:00",
    "equipment_category": "tile_cutter",
    "equipment_duration_days": 2,
    "maximum_distance_km": 25.0,
    "maximum_risk": "amber",
    "extraction_confidence": 0.85,
    "input_language": "ms-MY",
    "source_type": "voice_note",
    "notes": "Confirmed from structured AI extraction."
  }
}
```

Response body:

Use [examples/recommendation_response_tomorrow.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/recommendation_response_tomorrow.json) as the canonical example.

## POST /api/recommendations/recalculate

Purpose: recalculate a recommendation after a deadline change.

Status: future contract only

Request body:

```json
{
  "scenario_id": "three-hour-deadline",
  "revised_deadline_at": "2026-06-21T09:30:00+08:00"
}
```

Response body:

Use [examples/recommendation_response_three_hours.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/recommendation_response_three_hours.json) as the canonical example.

## POST /api/resources/material-passports

Purpose: convert a resource-photo extraction into a provisional or confirmed material passport.

Status: future contract only

Request body:

```json
{
  "request_id": "resource-site-a-001",
  "source_type": "resource_photo",
  "content_reference": "demo://resource/site-a-photo-001"
}
```

Response body:

Use [examples/site_a_material_passport.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/site_a_material_passport.json) as the standard successful example and [examples/site_e_provisional_passport.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/site_e_provisional_passport.json) as the manual-review example.

## POST /api/resources/equipment-passports

Purpose: convert a resource-photo extraction into a provisional equipment passport.

Status: future contract only

Response body:

Use [examples/site_d_equipment_passport.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/site_d_equipment_passport.json) as the canonical example.

## GET /api/resources

Purpose: list prepared material and equipment resources for the current cluster.

Status: future contract only

## GET /api/resources/{id}

Purpose: retrieve one stored material or equipment passport.

Status: future contract only

Use [examples/material_resource_passport.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/material_resource_passport.json) and [examples/equipment_resource_passport.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/equipment_resource_passport.json) as canonical examples.

## GET /api/evidence-records/{id}

Purpose: return the stored evidence record after human action.

Status: future contract only

Use [examples/evidence_record.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/evidence_record.json) as the canonical example.

## GET /api/health

Purpose: basic health check for future backend deployment.

Status: future contract only

Response body:

```json
{
  "status": "ok"
}
```

## AI Provider Notes

- The application depends on a provider interface, not a Grafilab-specific response shape.
- Official Grafilab endpoint and credential details were not present in this repository.
- The current implementation therefore uses a deterministic mock provider for offline tests and demos.
- Production Grafilab integration remains scaffolded only.
