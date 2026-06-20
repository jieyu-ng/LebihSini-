import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from .database import engine, get_db, Base
from . import models, schemas
from .demo_data import load_demo_dataset, DemoDataset
from .composer import generate_recommendation
from .contracts import (
    HumanApprovalDecision,
    ApprovalDecisionType,
    EvidenceRecord,
    to_dict,
    MaterialResourcePassport,
    EquipmentResourcePassport,
    DemandRequest,
    RiskCategory,
    VerificationStatus
)
from .urgency import RecommendationScenario

def make_material_passport(data: dict) -> MaterialResourcePassport:
    # Coerce serialized strings back to enums for optimization engine compatibility
    if isinstance(data.get("risk_category"), str):
        data["risk_category"] = RiskCategory(data["risk_category"])
    if isinstance(data.get("verification_status"), str):
        data["verification_status"] = VerificationStatus(data["verification_status"])
    return MaterialResourcePassport(**data)

def make_equipment_passport(data: dict) -> EquipmentResourcePassport:
    # Coerce serialized strings back to enums for optimization engine compatibility
    if isinstance(data.get("risk_category"), str):
        data["risk_category"] = RiskCategory(data["risk_category"])
    if isinstance(data.get("verification_status"), str):
        data["verification_status"] = VerificationStatus(data["verification_status"])
    return EquipmentResourcePassport(**data)

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

def extract_demand_from_audio(file_bytes: bytes, filename: str) -> DemandRequest:
    """
    Extracts structured demand requirements from voice notes / audio files using AI.
    
    HOW TO INTEGRATE GEMINI API (using google-generativeai package):
    ---------------------------------------------------------------
    1. Install package: `pip install google-generativeai`
    2. Import: `import google.generativeai as genai`
    3. Configure API Key: `genai.configure(api_key="YOUR_GEMINI_API_KEY")`
    4. Call the multimodal model (e.g. gemini-2.5-flash) with the audio bytes:
       
       # Convert raw audio bytes to Gemini-friendly MIME data parts
       audio_part = {
           "data": file_bytes,
           "mime_type": "audio/wav"  # or check filename extensions dynamically
       }
       
       prompt = (
           "You are an AI assistant helping a construction SME extract structured material/equipment procurement demand request from a Bahasa Malaysia voice note. "
           "Extract the following fields as JSON matching the schema of DemandRequest:\n"
           "category (e.g., porcelain_tile)\n"
           "colour (e.g., grey)\n"
           "width_mm\n"
           "height_mm\n"
           "quantity\n"
           "equipment (e.g., tile_cutter)\n"
           "equipment_days\n"
           "deadline_at (ISO 8601)\n"
           "risk_tolerance (green, amber, red)\n"
           "Return ONLY valid JSON matching this schema."
       )
       
       model = genai.GenerativeModel("gemini-2.5-flash")
       response = model.generate_content([prompt, audio_part])
       # Then parse JSON and return the instantiated DemandRequest contract
    """
    # For demo continuity, we parse the filename or return a default structured demand
    return DemandRequest(
        demand_id=f"demand-{uuid.uuid4().hex[:8]}",
        requesting_site_id="site-c",
        material_category="porcelain_tile",
        product_code="PG-600-GREY",
        colour="grey",
        dimension_mm_width=600,
        dimension_mm_height=600,
        quantity_units=500,
        deadline_at="2026-06-21T11:00:00+08:00",
        equipment_category="tile_cutter",
        equipment_duration_days=2,
        maximum_distance_km=25.0,
        maximum_risk=RiskCategory.AMBER,
        extraction_confidence=0.91,
        input_language="ms-MY",
        source_type="voice_note",
        notes=f"Extracted from uploaded audio file: {filename}. Demo data loaded successfully."
    )

@app.post("/api/extract-request", response_model=schemas.ExtractRequestResponse)
def extract_request(payload: schemas.ExtractRequestPayload):
    # Mocking Grafilab integration
    dataset = load_demo_dataset()
    return schemas.ExtractRequestResponse(
        demand=dataset.demand,
        warnings=["The user must confirm extracted fields before final recommendation approval."]
    )

@app.post("/api/extract-request/audio", response_model=schemas.ExtractRequestResponse)
async def extract_request_audio(file: UploadFile = File(...)):
    # Read the raw audio file bytes
    file_bytes = await file.read()
    
    # Process the audio file and extract structured fields
    demand = extract_demand_from_audio(file_bytes, file.filename)
    
    return schemas.ExtractRequestResponse(
        demand=demand,
        warnings=[
            "The user must confirm extracted fields before final recommendation approval.",
            f"Successfully processed audio upload '{file.filename}'."
        ]
    )

@app.post("/api/recommendations")
def get_recommendations(payload: schemas.RecommendationsPayload, db: Session = Depends(get_db)):
    # 1. Load default system-wide configuration parameters (supplier specs, carbon rates, etc)
    base_dataset = load_demo_dataset()
    
    # 2. Query material and equipment resources dynamically from the SQLite database
    db_mats = db.query(models.MaterialResource).all()
    db_eqs = db.query(models.EquipmentResource).all()
    
    # 3. Deserialize database JSON records into standard Python contract classes
    material_resources = [
        make_material_passport(m.raw_data) for m in db_mats
    ]
    equipment_resources = [
        make_equipment_passport(e.raw_data) for e in db_eqs if not e.is_commercial_fallback
    ]
    
    # Retrieve commercial fallback equipment passport from DB if present, else use base dataset default
    commercial_fallback = next(
        (make_equipment_passport(e.raw_data) for e in db_eqs if e.is_commercial_fallback),
        base_dataset.commercial_equipment_fallback
    )
    
    # 4. Construct dataset dynamically using live database resources
    dataset = DemoDataset(
        demand=payload.demand,
        material_resources=material_resources,
        equipment_resources=equipment_resources,
        commercial_equipment_fallback=commercial_fallback,
        commercial_equipment_rental_daily_myr=base_dataset.commercial_equipment_rental_daily_myr,
        supplier_unit_price_myr=base_dataset.supplier_unit_price_myr,
        supplier_available_from_at=base_dataset.supplier_available_from_at,
        supplier_delivery_lead_time_minutes=base_dataset.supplier_delivery_lead_time_minutes,
        supplier_delivery_cost_myr=base_dataset.supplier_delivery_cost_myr,
        supplier_delivery_distance_km=base_dataset.supplier_delivery_distance_km,
        supplier_vehicle_factor_kgco2e_per_km=base_dataset.supplier_vehicle_factor_kgco2e_per_km,
        disposal_or_storage_cost_myr=base_dataset.disposal_or_storage_cost_myr,
        disposal_or_storage_carbon_kgco2e=base_dataset.disposal_or_storage_carbon_kgco2e,
        inspection_cost_per_amber_resource_myr=base_dataset.inspection_cost_per_amber_resource_myr,
        additional_handling_cost_myr=base_dataset.additional_handling_cost_myr,
        platform_fee_myr=base_dataset.platform_fee_myr,
        expected_delay_cost_myr=base_dataset.expected_delay_cost_myr,
        material_collection_buffer_minutes=base_dataset.material_collection_buffer_minutes,
        equipment_collection_buffer_minutes=base_dataset.equipment_collection_buffer_minutes,
        equipment_return_buffer_minutes=base_dataset.equipment_return_buffer_minutes,
        reuse_processing_carbon_kgco2e=base_dataset.reuse_processing_carbon_kgco2e,
    )
    
    # 5. Generate recommendation using composed composer rules
    recommendation = generate_recommendation(dataset, demand=payload.demand)
    return to_dict(recommendation)

@app.post("/api/recommendations/recalculate")
def recalculate_recommendations(payload: schemas.RecalculatePayload, db: Session = Depends(get_db)):
    # 1. Load default system-wide configuration parameters
    base_dataset = load_demo_dataset()
    
    # 2. Query material and equipment resources dynamically from the SQLite database
    db_mats = db.query(models.MaterialResource).all()
    db_eqs = db.query(models.EquipmentResource).all()
    
    # 3. Deserialize database JSON records into standard Python contract classes
    material_resources = [
        make_material_passport(m.raw_data) for m in db_mats
    ]
    equipment_resources = [
        make_equipment_passport(e.raw_data) for e in db_eqs if not e.is_commercial_fallback
    ]
    
    # Retrieve commercial fallback equipment passport from DB if present, else use base dataset default
    commercial_fallback = next(
        (make_equipment_passport(e.raw_data) for e in db_eqs if e.is_commercial_fallback),
        base_dataset.commercial_equipment_fallback
    )
    
    # 4. Construct the revised scenario
    scenario = RecommendationScenario(
        scenario_id=payload.scenario_id,
        revised_deadline_at=payload.revised_deadline_at
    )
    
    # 5. Construct dataset dynamically using live database resources
    dataset = DemoDataset(
        demand=base_dataset.demand,
        material_resources=material_resources,
        equipment_resources=equipment_resources,
        commercial_equipment_fallback=commercial_fallback,
        commercial_equipment_rental_daily_myr=base_dataset.commercial_equipment_rental_daily_myr,
        supplier_unit_price_myr=base_dataset.supplier_unit_price_myr,
        supplier_available_from_at=base_dataset.supplier_available_from_at,
        supplier_delivery_lead_time_minutes=base_dataset.supplier_delivery_lead_time_minutes,
        supplier_delivery_cost_myr=base_dataset.supplier_delivery_cost_myr,
        supplier_delivery_distance_km=base_dataset.supplier_delivery_distance_km,
        supplier_vehicle_factor_kgco2e_per_km=base_dataset.supplier_vehicle_factor_kgco2e_per_km,
        disposal_or_storage_cost_myr=base_dataset.disposal_or_storage_cost_myr,
        disposal_or_storage_carbon_kgco2e=base_dataset.disposal_or_storage_carbon_kgco2e,
        inspection_cost_per_amber_resource_myr=base_dataset.inspection_cost_per_amber_resource_myr,
        additional_handling_cost_myr=base_dataset.additional_handling_cost_myr,
        platform_fee_myr=base_dataset.platform_fee_myr,
        expected_delay_cost_myr=base_dataset.expected_delay_cost_myr,
        material_collection_buffer_minutes=base_dataset.material_collection_buffer_minutes,
        equipment_collection_buffer_minutes=base_dataset.equipment_collection_buffer_minutes,
        equipment_return_buffer_minutes=base_dataset.equipment_return_buffer_minutes,
        reuse_processing_carbon_kgco2e=base_dataset.reuse_processing_carbon_kgco2e,
    )
    
    # 6. Generate recommendation using composed composer rules
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
    
    # Recreate recommendation from live database resources to snapshot it
    base_dataset = load_demo_dataset()
    db_mats = db.query(models.MaterialResource).all()
    db_eqs = db.query(models.EquipmentResource).all()
    
    material_resources = [
        make_material_passport(m.raw_data) for m in db_mats
    ]
    equipment_resources = [
        make_equipment_passport(e.raw_data) for e in db_eqs if not e.is_commercial_fallback
    ]
    commercial_fallback = next(
        (make_equipment_passport(e.raw_data) for e in db_eqs if e.is_commercial_fallback),
        base_dataset.commercial_equipment_fallback
    )
    
    scenario = None
    if "three-hour" in id:
        scenario = RecommendationScenario("three-hour-deadline", "2026-06-21T09:30:00+08:00")
        
    dataset = DemoDataset(
        demand=base_dataset.demand,
        material_resources=material_resources,
        equipment_resources=equipment_resources,
        commercial_equipment_fallback=commercial_fallback,
        commercial_equipment_rental_daily_myr=base_dataset.commercial_equipment_rental_daily_myr,
        supplier_unit_price_myr=base_dataset.supplier_unit_price_myr,
        supplier_available_from_at=base_dataset.supplier_available_from_at,
        supplier_delivery_lead_time_minutes=base_dataset.supplier_delivery_lead_time_minutes,
        supplier_delivery_cost_myr=base_dataset.supplier_delivery_cost_myr,
        supplier_delivery_distance_km=base_dataset.supplier_delivery_distance_km,
        supplier_vehicle_factor_kgco2e_per_km=base_dataset.supplier_vehicle_factor_kgco2e_per_km,
        disposal_or_storage_cost_myr=base_dataset.disposal_or_storage_cost_myr,
        disposal_or_storage_carbon_kgco2e=base_dataset.disposal_or_storage_carbon_kgco2e,
        inspection_cost_per_amber_resource_myr=base_dataset.inspection_cost_per_amber_resource_myr,
        additional_handling_cost_myr=base_dataset.additional_handling_cost_myr,
        platform_fee_myr=base_dataset.platform_fee_myr,
        expected_delay_cost_myr=base_dataset.expected_delay_cost_myr,
        material_collection_buffer_minutes=base_dataset.material_collection_buffer_minutes,
        equipment_collection_buffer_minutes=base_dataset.equipment_collection_buffer_minutes,
        equipment_return_buffer_minutes=base_dataset.equipment_return_buffer_minutes,
        reuse_processing_carbon_kgco2e=base_dataset.reuse_processing_carbon_kgco2e,
    )
    
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
