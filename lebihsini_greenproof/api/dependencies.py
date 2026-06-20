from __future__ import annotations

import os

from fastapi import Request

from lebihsini_greenproof.ai_provider import AIProvider
from lebihsini_greenproof.demo_data import DemoDataset, load_demo_dataset
from lebihsini_greenproof.grafilab_client import GrafilabClient
from lebihsini_greenproof.mock_grafilab_provider import MockGrafilabProvider
from lebihsini_greenproof.repositories.in_memory import InMemoryRepository
from lebihsini_greenproof.services.evidence_service import EvidenceService
from lebihsini_greenproof.services.extraction_service import ExtractionService, ServiceError
from lebihsini_greenproof.services.recommendation_service import RecommendationService


def get_repository(request: Request) -> InMemoryRepository:
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


def get_recommendation_service(request: Request) -> RecommendationService:
    return RecommendationService(get_repository(request), get_dataset(request))


def get_evidence_service(request: Request) -> EvidenceService:
    return EvidenceService(get_repository(request), get_dataset(request))


def build_runtime_state() -> dict:
    provider_mode = os.getenv("GREENPROOF_PROVIDER_MODE", "mock").strip().lower() or "mock"
    if provider_mode not in {"mock", "grafilab"}:
        provider_mode = "mock"
    return {
        "repository": InMemoryRepository(),
        "dataset": load_demo_dataset(),
        "provider_mode": provider_mode,
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
