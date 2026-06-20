from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lebihsini_greenproof.contracts import (
    AIExtractionRequest,
    DemandRequest,
    EquipmentResourcePassport,
    MaterialResourcePassport,
    RecommendationOutput,
    StructuredDemandExtractionResult,
    UserConfirmedExtraction,
)


@dataclass(slots=True)
class StoredExtraction:
    extraction_id: str
    request: AIExtractionRequest
    extraction: StructuredDemandExtractionResult


@dataclass(slots=True)
class StoredRecommendation:
    recommendation_id: str
    demand: DemandRequest
    recommendation: RecommendationOutput
    source_confirmation_id: str | None = None


class InMemoryRepository:
    """Deterministic in-memory state for the FastAPI MVP."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.extractions: dict[str, StoredExtraction] = {}
        self.confirmations: dict[str, UserConfirmedExtraction] = {}
        self.confirmation_demands: dict[str, DemandRequest] = {}
        self.material_passports: dict[str, MaterialResourcePassport] = {}
        self.equipment_passports: dict[str, EquipmentResourcePassport] = {}
        self.recommendations: dict[str, StoredRecommendation] = {}
        self.decisions: dict[str, dict[str, Any]] = {}
        self.evidence_records: dict[str, dict[str, Any]] = {}
        self._counters = {
            "extraction": 0,
            "confirmation": 0,
            "recommendation": 0,
            "decision": 0,
            "evidence": 0,
        }

    def _next_id(self, key: str, prefix: str) -> str:
        self._counters[key] += 1
        return f"{prefix}-{self._counters[key]:04d}"

    def next_extraction_id(self) -> str:
        return self._next_id("extraction", "ext")

    def next_confirmation_id(self) -> str:
        return self._next_id("confirmation", "cnf")

    def next_recommendation_id(self) -> str:
        return self._next_id("recommendation", "rec")

    def next_decision_id(self) -> str:
        return self._next_id("decision", "dec")

    def next_evidence_id(self) -> str:
        return self._next_id("evidence", "evd")

