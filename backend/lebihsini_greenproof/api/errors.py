from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from lebihsini_greenproof.services.extraction_service import ServiceError


def error_payload(code: str, message: str, details: dict | None = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details or {}}}


async def handle_service_error(_: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(exc.code, exc.message, exc.details),
    )


async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    if any("source_type" in ".".join(str(part) for part in error["loc"]) for error in errors):
        code = "UNSUPPORTED_INPUT_TYPE"
        message = "The submitted input source type is not supported."
    elif any(error["type"] == "missing" for error in errors):
        code = "MISSING_CRITICAL_FIELD"
        message = "One or more required fields are missing from the request."
    elif any("decision_type" in ".".join(str(part) for part in error["loc"]) for error in errors):
        code = "INVALID_DECISION"
        message = "The submitted decision type is not supported."
    else:
        code = "INTERNAL_ERROR"
        message = "The request body could not be validated."
    return JSONResponse(
        status_code=422,
        content=error_payload(code, message, {"validation_errors": errors}),
    )


async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=error_payload("INTERNAL_ERROR", "An unexpected internal error occurred.", {"exception_type": type(exc).__name__}),
    )
