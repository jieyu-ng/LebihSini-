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

    # ResourceRepository methods
    def list_materials(self) -> list[MaterialResourcePassport]:
        return list(self.material_passports.values())

    def list_equipment(self) -> list[EquipmentResourcePassport]:
        return list(self.equipment_passports.values())

    def get_material(self, resource_id: str) -> MaterialResourcePassport | None:
        return self.material_passports.get(resource_id)

    def get_equipment(self, resource_id: str) -> EquipmentResourcePassport | None:
        return self.equipment_passports.get(resource_id)

    # EvidenceRecordRepository methods
    def save(self, record_id: str, record_payload: dict, decided_by: str, decided_at: str, recommendation_id: str) -> None:
        self.evidence_records[record_id] = record_payload

    def get(self, record_id: str) -> dict | None:
        return self.evidence_records.get(record_id)
