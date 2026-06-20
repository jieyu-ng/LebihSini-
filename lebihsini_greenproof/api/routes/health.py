from __future__ import annotations

from fastapi import APIRouter, Request

from lebihsini_greenproof.contracts import CALCULATION_VERSION


router = APIRouter(tags=["health"])


@router.get("/health")
def get_health(request: Request) -> dict:
    provider_mode = request.app.state.provider_mode
    if provider_mode == "grafilab":
        provider_mode = "grafilab_configured"
    return {
        "status": "ok",
        "api_version": "v1",
        "calculation_version": CALCULATION_VERSION,
        "provider_mode": provider_mode,
        "storage_mode": "in_memory",
    }
