from __future__ import annotations

import os

from fastapi import APIRouter, Request

from lebihsini_greenproof.contracts import CALCULATION_VERSION


router = APIRouter(tags=["health"])


@router.get("/health")
def get_health(request: Request) -> dict:
    provider_mode = request.app.state.provider_mode
    provider_configured = provider_mode == "mock"
    if provider_mode == "grafilab":
        provider_configured = bool(os.getenv(request.app.state.provider_api_key_env_var))
    return {
        "status": "ok",
        "api_version": "v1",
        "calculation_version": CALCULATION_VERSION,
        "provider_mode": provider_mode,
        "provider_configured": provider_configured,
        "provider_model": "mock_grafilab" if provider_mode == "mock" else request.app.state.provider_text_model,
        "storage_mode": "in_memory",
    }
