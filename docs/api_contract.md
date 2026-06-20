# LebihSini GreenProof API Contract

All request and response shapes use canonical `snake_case`. The FastAPI backend is now implemented as an in-memory MVP orchestration layer over the existing deterministic modules.

Units:

- quantity: units
- dimensions: millimetres
- distance: kilometres
- travel time: minutes
- money: Malaysian ringgit
- carbon: kgCO2e
- confidence: decimal between `0.0` and `1.0`
- datetime: ISO 8601

## Common Error Shape

```json
{
  "error": {
    "code": "MISSING_CRITICAL_FIELD",
    "message": "Quantity must be confirmed before generating a recommendation.",
    "details": {}
  }
}
```

Standard error codes:

- `INPUT_UNREADABLE`
- `UNSUPPORTED_INPUT_TYPE`
- `MISSING_CRITICAL_FIELD`
- `LOW_CONFIDENCE_CONFIRMATION_REQUIRED`
- `AI_PROVIDER_UNAVAILABLE`
- `INVALID_PROVIDER_OUTPUT`
- `MANUAL_INSPECTION_REQUIRED`
- `RESOURCE_NOT_FOUND`
- `RECOMMENDATION_NOT_FOUND`
- `EVIDENCE_RECORD_NOT_FOUND`
- `INVALID_DECISION`
- `INTERNAL_ERROR`

## GET /api/health

Status: implemented

Returns:

- service status
- API version
- calculation version
- provider mode
- storage mode

Notes:

- state is in-memory only
- default provider mode is `mock`

## POST /api/extract-request

Status: implemented

Request model:

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

Response model:

- `extraction_id`
- `extracted_fields`
- `missing_fields`
- `missing_critical_fields`
- `warnings`
- `provider_metadata`
- `confirmation_status`
- `can_proceed_to_confirmation`
- `requires_manual_review`
- `normalized_demand`

Example:

- [examples/bahasa_voice_extraction.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/bahasa_voice_extraction.json)

Confirmation requirement:

- raw provider output must still be confirmed before optimisation

## POST /api/extractions/{extraction_id}/confirm

Status: implemented

Request model:

```json
{
  "action": "accept",
  "confirmed_values": {
    "product_code": "PG-600-GREY"
  },
  "confirmed_at": "2026-06-20T09:05:00+08:00"
}
```

Response model:

- `confirmation_id`
- `status`
- `confirmed_fields`
- `warnings`
- `confirmed_demand` when validation succeeds

Example:

- [examples/confirmed_demand.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/confirmed_demand.json)

Confirmation requirement:

- unresolved critical fields return `MISSING_CRITICAL_FIELD`

## POST /api/material-passports

Status: implemented

Request model:

```json
{
  "request_id": "resource-site-a-001",
  "source_type": "resource_photo",
  "content": "site a photo",
  "content_reference": "demo://resource/site-a-photo-001",
  "input_language": "en-MY",
  "resource_id": "mat-site-a-tiles"
}
```

Response model:

- `request_id`
- `resource_kind`
- `can_enter_automatic_matching`
- `requires_manual_review`
- `warnings`
- `generated_material_passport`

Examples:

- [examples/site_a_material_passport.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/site_a_material_passport.json)
- [examples/site_e_provisional_passport.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/site_e_provisional_passport.json)

Notes:

- Site E remains manual-review only
- state is stored in-memory for the running process

## POST /api/equipment-passports

Status: implemented

Request model:

```json
{
  "request_id": "resource-site-d-001",
  "source_type": "resource_photo",
  "content": "site d photo",
  "content_reference": "demo://resource/site-d-photo-001",
  "input_language": "en-MY",
  "resource_id": "eq-site-d-cutter"
}
```

Response model:

- `request_id`
- `resource_kind`
- `can_enter_automatic_matching`
- `requires_manual_review`
- `warnings`
- `generated_equipment_passport`

Example:

- [examples/site_d_equipment_passport.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/site_d_equipment_passport.json)

## GET /api/resources

Status: implemented

Query filters:

- `resource_type`
- `material_category`
- `equipment_category`
- `risk_category`
- `verification_status`
- `site_id`
- `automatic_matching_eligibility`

Response model:

```json
{
  "items": [],
  "storage_mode": "in_memory",
  "count": 0
}
```

Notes:

- uses the demo dataset plus any in-memory generated passports

## GET /api/resources/{resource_id}

Status: implemented

Returns one material or equipment resource.

Errors:

- `RESOURCE_NOT_FOUND`

## POST /api/recommendations

Status: implemented

Request model:

```json
{
  "confirmed_demand_id": "cnf-0001"
}
```

Alternative request model:

```json
{
  "confirmed_demand": {
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

Response model:

- full `RecommendationOutput`

Examples:

- [examples/recommendation_response_tomorrow.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/recommendation_response_tomorrow.json)

Confirmation requirement:

- raw unconfirmed extraction output cannot be used here

## POST /api/recommendations/{recommendation_id}/recalculate

Status: implemented

Request model:

```json
{
  "revised_deadline_at": "2026-06-21T09:30:00+08:00"
}
```

Response model:

- full recalculated `RecommendationOutput`

Example:

- [examples/recommendation_response_three_hours.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/recommendation_response_three_hours.json)

## POST /api/recommendations/{recommendation_id}/decision

Status: implemented

Request model:

```json
{
  "decision_type": "approve",
  "actor_reference": "demo.user@lebihsini.test",
  "decided_at": "2026-06-20T12:05:00+08:00",
  "override_notes": "Approved after checking Site B inspection condition.",
  "modified_plan_details": {}
}
```

Supported decisions:

- `approve`
- `modify`
- `reject`
- `proceed_with_normal_procurement`
- `request_inspection`

Response model:

- `decision`
- `evidence_record`

Notes:

- human decision is mandatory
- state is stored in-memory only

## GET /api/evidence-records/{record_id}

Status: implemented

Response model includes:

- `name` set to `GreenProof Evidence Record`
- original request
- extraction result and evidence
- confirmed demand
- resources considered, selected, excluded
- cost and carbon comparison
- recommendation
- user decision
- final approved plan
- calculation version
- provider metadata when available

Errors:

- `EVIDENCE_RECORD_NOT_FOUND`

Example:

- [examples/evidence_record.json](C:/Users/ganka/Downloads/Imagine/LebihSini-/examples/evidence_record.json)

## Provider Notes

- mock-provider mode is the default for tests and demos
- real Grafilab integration remains scaffolded only
- no Grafilab endpoints were invented in this implementation
- all backend state is explicitly in-memory
