from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from lebihsini_greenproof.api.app import create_app


def main() -> None:
    client = TestClient(create_app())

    health = client.get("/api/health").json()
    extraction = client.post(
        "/api/extract-request",
        json={
            "request_id": "demo-bm-001",
            "source_type": "voice_note",
            "content": "Esok perlukan 500 tile kelabu 600 kali 600 dan mesin pemotong untuk dua hari.",
            "content_reference": "demo://voice-note/site-c/request-001",
            "input_language": "ms-MY",
            "reference_datetime": "2026-06-20T09:00:00+08:00",
        },
    ).json()
    confirmation = client.post(
        f"/api/extractions/{extraction['extraction_id']}/confirm",
        json={
            "action": "accept",
            "confirmed_values": {"product_code": "PG-600-GREY"},
            "confirmed_at": "2026-06-20T09:05:00+08:00",
        },
    ).json()
    recommendation = client.post(
        "/api/recommendations",
        json={"confirmed_demand_id": confirmation["confirmation_id"]},
    ).json()
    urgency = client.post(
        f"/api/recommendations/{recommendation['recommendation_id']}/recalculate",
        json={"revised_deadline_at": "2026-06-21T09:30:00+08:00"},
    ).json()
    decision = client.post(
        f"/api/recommendations/{recommendation['recommendation_id']}/decision",
        json={
            "decision_type": "approve",
            "actor_reference": "demo.user@lebihsini.test",
            "decided_at": "2026-06-20T12:05:00+08:00",
            "override_notes": "Approved after checking Site B inspection condition.",
        },
    ).json()
    evidence = client.get(
        f"/api/evidence-records/{decision['evidence_record']['record_id']}"
    ).json()
    site_e_passport = client.post(
        "/api/material-passports",
        json={
            "request_id": "site-e-demo-001",
            "source_type": "resource_photo",
            "content": "site e",
            "content_reference": "demo://resource/site-e-photo-001",
            "input_language": "en-MY",
            "resource_id": "mat-site-e-tiles",
        },
    ).json()

    print(
        json.dumps(
            {
                "health": health,
                "extraction_id": extraction["extraction_id"],
                "recommendation_id": recommendation["recommendation_id"],
                "tomorrow_materials": {
                    item["site_id"]: item["quantity_units"]
                    for item in recommendation["selected_material_resources"]
                },
                "tomorrow_supplier_shortfall_units": recommendation["supplier_shortfall_units"],
                "urgent_materials": {
                    item["site_id"]: item["quantity_units"]
                    for item in urgency["selected_material_resources"]
                },
                "urgent_supplier_shortfall_units": urgency["supplier_shortfall_units"],
                "evidence_record_name": evidence["name"],
                "site_e_requires_manual_review": site_e_passport["requires_manual_review"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
