# LebihSini GreenProof API Contract

All endpoints below are defined as MVP contracts for frontend/backend alignment. They are not implemented yet in this repository unless explicitly noted.

## Common Error Shape

```json
{
  "error": {
    "code": "DEADLINE_INFEASIBLE",
    "message": "No prepared reuse source can meet the selected deadline.",
    "details": {}
  }
}
```

Units:

- quantity: units
- dimensions: millimetres
- distance: kilometres
- travel time: minutes
- money: Malaysian ringgit
- carbon: kgCO2e
- confidence: decimal between 0.0 and 1.0
- datetime: ISO 8601

## POST /api/extract-request

Purpose: convert uploaded or raw unstructured input into a structured demand request.

Status: future contract only

Request body:

```json
{
  "sourceType": "voice_note",
  "inputLanguage": "ms-MY",
  "contentReference": "demo://voice-note/site-c/request-001"
}
```

Response body:

```json
{
  "demand": {
    "demand_id": "demand-site-c-001",
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
    "extraction_confidence": 0.91,
    "input_language": "ms-MY",
    "source_type": "voice_note",
    "notes": "Demo demand extracted from a Bahasa voice note."
  },
  "warnings": [
    "The user must confirm extracted fields before final recommendation approval."
  ]
}
```

Required fields:

- `sourceType`
- `contentReference`

Optional fields:

- `inputLanguage`

## POST /api/recommendations

Purpose: generate a recommendation from a confirmed demand request.

Status: future contract only

Request body:

```json
{
  "demand": {
    "demand_id": "demand-site-c-001",
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
    "extraction_confidence": 0.91,
    "input_language": "ms-MY",
    "source_type": "voice_note",
    "notes": "Demo demand extracted from a Bahasa voice note."
  }
}
```

Response body:

```json
{
  "recommendation_id": "rec-tomorrow-deadline",
  "verdict": "partial_reuse_recommended",
  "deadline_met": true,
  "selected_material_resources": [
    {
      "resource_id": "mat-site-a-tiles",
      "site_id": "site-a",
      "site_name": "Site A - Puchong Utama",
      "quantity_units": 300,
      "transfer_price_myr_per_unit": 3.2,
      "distance_km": 11.0,
      "inspection_required": false,
      "conditions": []
    },
    {
      "resource_id": "mat-site-b-tiles",
      "site_id": "site-b",
      "site_name": "Site B - Bandar Puteri",
      "quantity_units": 130,
      "transfer_price_myr_per_unit": 3.0,
      "distance_km": 17.0,
      "inspection_required": true,
      "conditions": [
        "Manual inspection required before this resource can be approved."
      ]
    }
  ],
  "selected_equipment": {
    "resource_id": "eq-site-d-cutter",
    "site_id": "site-d",
    "site_name": "Site D - Subang Jaya",
    "category": "tile_cutter",
    "duration_days": 2,
    "rental_cost_myr": 120.0,
    "conditions": []
  },
  "excluded_resources": [
    {
      "resource_id": "mat-site-e-tiles",
      "site_id": "site-e",
      "site_name": "Site E - Kinrara",
      "reason_code": "material_ineligible",
      "reason_text": "Risk exceeds the allowed tolerance. Excluded from automatic recommendation because required documentation was absent. Excluded from automatic recommendation because the product label was unreadable and the condition could not be sufficiently verified.",
      "confidence": 0.41
    }
  ],
  "supplier_shortfall_units": 70,
  "quantity_fulfilled_units": 500,
  "conditions": [
    "Manual inspection required before this resource can be approved.",
    "Supplier fallback added to fulfil the remaining quantity."
  ]
}
```

## POST /api/recommendations/recalculate

Purpose: recalculate a recommendation after urgency or business-rule changes.

Status: future contract only

Request body:

```json
{
  "scenario_id": "three-hour-deadline",
  "lead_time_limit_minutes": 45
}
```

Response body:

```json
{
  "recommendation_id": "rec-three-hour-deadline",
  "verdict": "partial_reuse_recommended",
  "deadline_met": true,
  "supplier_shortfall_units": 200,
  "assumptions": [
    "Estimated using stated cost and carbon assumptions.",
    "This reference flow is a foundation validator, not the final optimiser."
  ]
}
```

Note: the current three-hour response is still a demo expected output generated by the reference scaffold, not by the completed optimiser.

## POST /api/recommendations/{id}/decision

Purpose: capture approval, modification, rejection, or inspection requests for a recommendation.

Status: future contract only

Request body:

```json
{
  "decision_id": "decision-001",
  "recommendation_id": "rec-tomorrow-deadline",
  "decision_type": "approve",
  "decided_by": "demo.user@lebihsini.test",
  "decided_at": "2026-06-20T12:05:00+08:00",
  "override_notes": "Approved after confirming Site B inspection condition."
}
```

Response body:

```json
{
  "status": "recorded",
  "decision_id": "decision-001"
}
```

## GET /api/resources

Purpose: list prepared material and equipment resources for the current cluster.

Status: future contract only

Response body:

```json
{
  "items": [
    {
      "resource_id": "mat-site-a-tiles",
      "site_id": "site-a",
      "site_name": "Site A - Puchong Utama",
      "category": "porcelain_tile",
      "quantity_units": 300,
      "risk_category": "green",
      "verification_status": "verified"
    }
  ]
}
```

## GET /api/resources/{id}

Purpose: retrieve a full material or equipment passport.

Status: future contract only

Response body example:

```json
{
  "resource_id": "eq-site-d-cutter",
  "site_id": "site-d",
  "site_name": "Site D - Subang Jaya",
  "category": "tile_cutter",
  "brand_model": "Hilti DC-600 Demo",
  "owner": "Site D",
  "availability_start_at": "2026-06-20T08:00:00+08:00",
  "availability_end_at": "2026-06-23T18:00:00+08:00",
  "collection_window_start_at": "2026-06-21T08:00:00+08:00",
  "collection_window_end_at": "2026-06-21T09:00:00+08:00",
  "rental_rate_myr_per_day": 60.0,
  "commercial_rental_rate_myr_per_day": 120.0,
  "distance_to_site_km": 9.0,
  "travel_time_to_site_minutes": 30,
  "transport_rate_myr_per_km": 4.0,
  "vehicle_factor_kgco2e_per_km": 0.27,
  "maintenance_record_present": true,
  "maintenance_confidence": 0.92,
  "operator_required": false,
  "risk_category": "green",
  "verification_status": "verified",
  "evidence_notes": [
    "Maintenance record present.",
    "Available for three days."
  ]
}
```

## GET /api/evidence-records/{id}

Purpose: return the stored evidence record after human action.

Status: future contract only

Response body:

```json
{
  "record_id": "evidence-001",
  "original_request_reference": "demo://voice-note/site-c/request-001",
  "expected_impact_summary": "Reuse 430 tiles, purchase 70 new tiles, and use the nearby idle cutter while keeping the deadline feasible."
}
```

## GET /api/health

Purpose: basic health check for future backend deployment.

Status: future contract only

Response body:

```json
{
  "status": "ok"
}
```
