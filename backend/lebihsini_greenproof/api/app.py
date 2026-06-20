from __future__ import annotations

import logging
import time
import uuid

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from lebihsini_greenproof.api.dependencies import build_runtime_state
from lebihsini_greenproof.api.errors import (
    handle_service_error,
    handle_unexpected_error,
    handle_validation_error,
)
from lebihsini_greenproof.api.routes.confirmation import router as confirmation_router
from lebihsini_greenproof.api.routes.decisions import router as decisions_router
from lebihsini_greenproof.api.routes.extraction import router as extraction_router
from lebihsini_greenproof.api.routes.health import router as health_router
from lebihsini_greenproof.api.routes.passports import router as passports_router
from lebihsini_greenproof.api.routes.recommendations import router as recommendations_router
from lebihsini_greenproof.api.routes.resources import router as resources_router
from lebihsini_greenproof.services.extraction_service import ServiceError


logger = logging.getLogger("lebihsini_greenproof.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB safely
    if app.state.resource_store == "sqlite":
        from ..db.database import engine, Base
        from ..db.models import MaterialResource, EquipmentResource
        from sqlalchemy.orm import Session
        import os
        
        # Ensure directory exists if sqlite file is in a dir
        db_url = os.getenv("GREENPROOF_DATABASE_URL", "sqlite:///./data/greenproof_demo.db")
        if db_url.startswith("sqlite:///"):
            path = db_url.replace("sqlite:///", "")
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                
        Base.metadata.create_all(bind=engine)
        
        # Idempotent seed
        with Session(engine) as session:
            mat_count = session.query(MaterialResource).count()
            eq_count = session.query(EquipmentResource).count()
            if mat_count == 0 and eq_count == 0:
                dataset = app.state.dataset
                for m in dataset.material_resources:
                    session.add(MaterialResource.from_domain(m))
                for e in dataset.equipment_resources:
                    session.add(EquipmentResource.from_domain(e))
                session.add(EquipmentResource.from_domain(dataset.commercial_equipment_fallback))
                session.commit()
    yield

def create_app() -> FastAPI:
    runtime_state = build_runtime_state()
    app = FastAPI(title="LebihSini GreenProof API", version="1.0.0", lifespan=lifespan)
    app.state.resource_store = runtime_state.get("resource_store", "in_memory")
    app.state.repository = runtime_state["repository"]
    app.state.dataset = runtime_state["dataset"]
    app.state.provider_mode = runtime_state["provider_mode"]
    app.state.provider_api_key_env_var = runtime_state["provider_api_key_env_var"]
    app.state.provider_base_url = runtime_state["provider_base_url"]
    app.state.provider_text_model = runtime_state["provider_text_model"]
    app.state.provider_timeout_seconds = runtime_state["provider_timeout_seconds"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=runtime_state["cors_origins"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        started = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_id=%s endpoint=%s status=%s duration_ms=%s provider_mode=%s",
            request_id,
            request.url.path,
            response.status_code,
            duration_ms,
            request.app.state.provider_mode,
        )
        return response

    app.add_exception_handler(ServiceError, handle_service_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(Exception, handle_unexpected_error)

    app.include_router(health_router, prefix="/api")
    app.include_router(extraction_router, prefix="/api")
    app.include_router(confirmation_router, prefix="/api")
    app.include_router(passports_router, prefix="/api")
    app.include_router(resources_router, prefix="/api")
    app.include_router(recommendations_router, prefix="/api")
    app.include_router(decisions_router, prefix="/api")
    return app


app = create_app()
