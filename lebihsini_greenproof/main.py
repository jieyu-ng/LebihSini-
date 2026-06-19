import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from .database import engine, get_db, Base
from . import models, schemas
from .demo_data import load_demo_dataset
from .composer import generate_recommendation
from .contracts import (
    HumanApprovalDecision,
    ApprovalDecisionType,
    EvidenceRecord,
    to_dict
)
from .urgency import RecommendationScenario

# Lifecycle hook to seed the database
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Seed the database if empty
    db = next(get_db())
    if db.query(models.MaterialResource).count() == 0:
        dataset = load_demo_dataset()
        for mat in dataset.material_resources:
            db.add(models.MaterialResource(
                resource_id=mat.resource_id,
                site_id=mat.site_id,
                category=mat.category,
                quantity_units=mat.quantity_units,
                risk_category=mat.risk_category,
                verification_status=mat.verification_status,
                raw_data=to_dict(mat)
            ))
        for eq in dataset.equipment_resources:
            db.add(models.EquipmentResource(
                resource_id=eq.resource_id,
                site_id=eq.site_id,
                category=eq.category,
                is_commercial_fallback=eq.is_commercial_fallback,
                verification_status=eq.verification_status,
                raw_data=to_dict(eq)
            ))
        db.add(models.EquipmentResource(
            resource_id=dataset.commercial_equipment_fallback.resource_id,
            site_id=dataset.commercial_equipment_fallback.site_id,
            category=dataset.commercial_equipment_fallback.category,
            is_commercial_fallback=True,
            verification_status=dataset.commercial_equipment_fallback.verification_status,
            raw_data=to_dict(dataset.commercial_equipment_fallback)
        ))
        db.commit()
    db.close()
    yield

app = FastAPI(title="LebihSini GreenProof API", lifespan=lifespan)

@app.get("/api/health", response_model=schemas.HealthResponse)
def health_check():
    return schemas.HealthResponse(status="ok")

@app.post("/api/extract-request", response_model=schemas.ExtractRequestResponse)
def extract_request(payload: schemas.ExtractRequestPayload):
    # Mocking Grafilab integration
    dataset = load_demo_dataset()
    return schemas.ExtractRequestResponse(
        demand=dataset.demand,
        warnings=["The user must confirm extracted fields before final recommendation approval."]
    )

@app.post("/api/recommendations")
def get_recommendations(payload: schemas.RecommendationsPayload):
    dataset = load_demo_dataset()
    recommendation = generate_recommendation(dataset, demand=payload.demand)
    return to_dict(recommendation)

@app.post("/api/recommendations/recalculate")
def recalculate_recommendations(payload: schemas.RecalculatePayload):
    dataset = load_demo_dataset()
    scenario = RecommendationScenario(
        scenario_id=payload.scenario_id,
        revised_deadline_at=payload.revised_deadline_at
    )
    recommendation = generate_recommendation(dataset, dataset.demand, scenario)
    return to_dict(recommendation)

@app.post("/api/recommendations/{id}/decision")
def capture_decision(id: str, payload: schemas.DecisionPayload, db: Session = Depends(get_db)):
    # Create the HumanApprovalDecision
    decision = HumanApprovalDecision(
        decision_id=payload.decision_id,
        recommendation_id=payload.recommendation_id,
        decision_type=ApprovalDecisionType(payload.decision_type),
        decided_by=payload.decided_by,
        decided_at=payload.decided_at,
        override_notes=payload.override_notes
    )
    
    # Recreate recommendation to snapshot it
    dataset = load_demo_dataset()
    scenario = None
    if "three-hour" in id:
        scenario = RecommendationScenario("three-hour-deadline", "2026-06-21T09:30:00+08:00")
        
    recommendation = generate_recommendation(dataset, dataset.demand, scenario)
    
    # Generate Evidence Record
    evidence_record = EvidenceRecord(
        record_id=f"ev-{payload.decision_id}",
        demand=dataset.demand,
        recommendation=recommendation,
        original_request_reference="demo://voice-note/site-c/request-001",
        resources_considered=[r.resource_id for r in dataset.material_resources] + [r.resource_id for r in dataset.equipment_resources],
        human_decision=decision,
        overrides=[payload.override_notes] if payload.override_notes else [],
        expected_impact_summary=f"Expected to avoid {recommendation.carbon_breakdown.net_carbon_avoided_kgco2e} kgCO2e and save {recommendation.cost_breakdown.net_saving_myr} MYR"
    )
    
    # Persist
    db_record = models.EvidenceRecord(
        record_id=evidence_record.record_id,
        recommendation_id=recommendation.recommendation_id,
        decided_by=decision.decided_by,
        decided_at=decision.decided_at,
        raw_data=to_dict(evidence_record)
    )
    db.add(db_record)
    db.commit()
    
    return schemas.DecisionResponse(status="recorded", decision_id=payload.decision_id)

@app.get("/api/resources")
def list_resources(db: Session = Depends(get_db)):
    mats = db.query(models.MaterialResource).all()
    eqs = db.query(models.EquipmentResource).all()
    
    items = []
    for m in mats:
        items.append({
            "resource_id": m.resource_id,
            "site_id": m.site_id,
            "site_name": m.raw_data.get("site_name"),
            "category": m.category,
            "quantity_units": m.quantity_units,
            "risk_category": m.risk_category,
            "verification_status": m.verification_status
        })
    for e in eqs:
        items.append({
            "resource_id": e.resource_id,
            "site_id": e.site_id,
            "site_name": e.raw_data.get("site_name"),
            "category": e.category,
            "is_commercial_fallback": e.is_commercial_fallback,
            "verification_status": e.verification_status
        })
        
    return {"items": items}

@app.get("/api/resources/{id}")
def get_resource(id: str, db: Session = Depends(get_db)):
    mat = db.query(models.MaterialResource).filter(models.MaterialResource.resource_id == id).first()
    if mat:
        return mat.raw_data
    eq = db.query(models.EquipmentResource).filter(models.EquipmentResource.resource_id == id).first()
    if eq:
        return eq.raw_data
    raise HTTPException(status_code=404, detail="Resource not found")

@app.get("/api/evidence-records/{id}")
def get_evidence_record(id: str, db: Session = Depends(get_db)):
    record = db.query(models.EvidenceRecord).filter(models.EvidenceRecord.record_id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Evidence record not found")
    return record.raw_data
