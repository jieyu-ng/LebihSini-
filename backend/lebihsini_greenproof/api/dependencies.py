from __future__ import annotations

import os

from fastapi import Request, Depends

from lebihsini_greenproof.ai_provider import AIProvider
from lebihsini_greenproof.demo_data import DemoDataset, load_demo_dataset
from lebihsini_greenproof.grafilab_client import GrafilabClient
from lebihsini_greenproof.mock_grafilab_provider import MockGrafilabProvider
from lebihsini_greenproof.repositories.in_memory import InMemoryRepository
from lebihsini_greenproof.services.evidence_service import EvidenceService
from lebihsini_greenproof.services.extraction_service import ExtractionService, ServiceError
from lebihsini_greenproof.services.recommendation_service import RecommendationService

def get_db():
    from lebihsini_greenproof.db.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_repository(request: Request) -> InMemoryRepository:
    # Always return InMemoryRepository for workflow state (extractions, confirmations)
    return request.app.state.repository


def get_dataset(request: Request) -> DemoDataset:
    return request.app.state.dataset


def get_provider(request: Request) -> AIProvider:
    mode = request.app.state.provider_mode
    if mode == "mock":
        return MockGrafilabProvider()
    client = GrafilabClient(
        api_key_env_var=request.app.state.provider_api_key_env_var,
        base_url=request.app.state.provider_base_url,
        text_model=request.app.state.provider_text_model,
        timeout_seconds=request.app.state.provider_timeout_seconds,
    )
    if not client.api_key:
        raise ServiceError(
            "AI_PROVIDER_UNAVAILABLE",
            f"Real provider mode is configured but `{request.app.state.provider_api_key_env_var}` is not set.",
            status_code=503,
        )
    return client


def get_extraction_service(request: Request) -> ExtractionService:
    return ExtractionService(get_repository(request), get_dataset(request), get_provider(request))


def get_resource_repository(request: Request, db=Depends(get_db)):
    if request.app.state.resource_store == "sqlite":
        from lebihsini_greenproof.repositories.sqlite_repository import SQLiteRepository
        return SQLiteRepository(db)
    return request.app.state.repository

def get_evidence_repository(request: Request, db=Depends(get_db)):
    if request.app.state.resource_store == "sqlite":
        from lebihsini_greenproof.repositories.sqlite_repository import SQLiteRepository
        return SQLiteRepository(db)
    return request.app.state.repository

def get_recommendation_service(
    request: Request,
    resource_repo=Depends(get_resource_repository)
) -> RecommendationService:
    return RecommendationService(
        get_repository(request), 
        get_dataset(request), 
        resource_repository=resource_repo
    )

def get_evidence_service(
    request: Request,
    evidence_repo=Depends(get_evidence_repository)
) -> EvidenceService:
    return EvidenceService(
        get_repository(request), 
        get_dataset(request),
        evidence_repository=evidence_repo
    )


def build_runtime_state() -> dict:
    provider_mode = os.getenv("GREENPROOF_PROVIDER_MODE", "mock").strip().lower() or "mock"
    if provider_mode not in {"mock", "grafilab"}:
        provider_mode = "mock"
    
    resource_store = os.getenv("GREENPROOF_RESOURCE_STORE", "in_memory").strip().lower() or "in_memory"
    if resource_store not in {"in_memory", "sqlite"}:
        resource_store = "in_memory"

    dataset = load_demo_dataset()
    repository = InMemoryRepository()
    
    # Prepopulate in-memory repo with demo data so tests and in_memory mode work
    for m in dataset.material_resources:
        repository.material_passports[m.resource_id] = m
    for e in dataset.equipment_resources:
        repository.equipment_passports[e.resource_id] = e
    repository.equipment_passports[dataset.commercial_equipment_fallback.resource_id] = dataset.commercial_equipment_fallback

    return {
        "repository": repository,
        "dataset": dataset,
        "provider_mode": provider_mode,
        "resource_store": resource_store,
        "provider_api_key_env_var": os.getenv("GREENPROOF_PROVIDER_API_KEY_ENV", "GRAFILAB_API_KEY"),
        "provider_base_url": os.getenv("GRAFILAB_BASE_URL", "https://console-api.grafilab.ai/api/oai/v1"),
        "provider_text_model": os.getenv("GRAFILAB_TEXT_MODEL", "grafilab/qwen3.6-flash"),
        "provider_timeout_seconds": float(os.getenv("GRAFILAB_TIMEOUT_SECONDS", "15.0")),
        "cors_origins": [
            origin.strip()
            for origin in os.getenv("GREENPROOF_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
            if origin.strip()
        ],
    }
