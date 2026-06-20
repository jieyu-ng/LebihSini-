from typing import Protocol, Optional, List
from ..contracts import MaterialResourcePassport, EquipmentResourcePassport, EvidenceRecord

class ResourceRepository(Protocol):
    def list_materials(self) -> List[MaterialResourcePassport]:
        ...

    def list_equipment(self) -> List[EquipmentResourcePassport]:
        ...

    def get_material(self, resource_id: str) -> Optional[MaterialResourcePassport]:
        ...

    def get_equipment(self, resource_id: str) -> Optional[EquipmentResourcePassport]:
        ...

class EvidenceRecordRepository(Protocol):
    def save(self, record_id: str, record_payload: dict, decided_by: str, decided_at: str, recommendation_id: str) -> None:
        ...

    def get(self, record_id: str) -> Optional[dict]:
        ...

class WorkflowRepository(Protocol):
    # This interface is implicitly what InMemoryRepository satisfies for extractions, confirmations, etc.
    # We leave it flexible as services only typehint InMemoryRepository for workflow right now,
    # or we can keep services depending directly on InMemoryRepository for workflow state.
    pass
