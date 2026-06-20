from __future__ import annotations

from fastapi import APIRouter, Depends

from lebihsini_greenproof.api.models import ExtractRequestBody
from lebihsini_greenproof.contracts import AIExtractionRequest
from lebihsini_greenproof.serialization import to_jsonable
from lebihsini_greenproof.services.extraction_service import ExtractionService
from lebihsini_greenproof.api.dependencies import get_extraction_service


router = APIRouter(tags=["extraction"])


@router.post("/extract-request")
def extract_request(
    body: ExtractRequestBody,
    service: ExtractionService = Depends(get_extraction_service),
) -> dict:
    extraction_id, result = service.create_extraction(AIExtractionRequest(**body.model_dump()))
    payload = to_jsonable(result)
    payload["extraction_id"] = extraction_id
    payload["confirmation_status"] = "pending"
    payload["provider_metadata"] = payload.pop("model_metadata")
    payload["missing_critical_fields"] = payload["missing_fields"]
    return payload
