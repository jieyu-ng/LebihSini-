from __future__ import annotations

from fastapi import APIRouter, Depends

from lebihsini_greenproof.api.dependencies import get_extraction_service
from lebihsini_greenproof.api.models import ConfirmExtractionBody
from lebihsini_greenproof.serialization import to_jsonable
from lebihsini_greenproof.services.extraction_service import ExtractionService


router = APIRouter(tags=["confirmation"])


@router.post("/extractions/{extraction_id}/confirm")
def confirm_extraction(
    extraction_id: str,
    body: ConfirmExtractionBody,
    service: ExtractionService = Depends(get_extraction_service),
) -> dict:
    confirmation_id, result = service.confirm_extraction(
        extraction_id,
        action=body.action,
        confirmed_values=body.confirmed_values,
        confirmed_at=body.confirmed_at,
    )
    payload = to_jsonable(result)
    payload["confirmation_id"] = confirmation_id
    return payload
