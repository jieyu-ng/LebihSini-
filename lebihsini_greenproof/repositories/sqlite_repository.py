from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import MaterialResource, EquipmentResource, EvidenceRecord as DBEvidenceRecord
from ..contracts import MaterialResourcePassport, EquipmentResourcePassport, EvidenceRecord

class SQLiteRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_materials(self) -> List[MaterialResourcePassport]:
        records = self.db.query(MaterialResource).all()
        return [r.to_domain() for r in records]

    def list_equipment(self) -> List[EquipmentResourcePassport]:
        records = self.db.query(EquipmentResource).all()
        return [r.to_domain() for r in records]

    def get_material(self, resource_id: str) -> Optional[MaterialResourcePassport]:
        record = self.db.query(MaterialResource).filter(MaterialResource.resource_id == resource_id).first()
        return record.to_domain() if record else None

    def get_equipment(self, resource_id: str) -> Optional[EquipmentResourcePassport]:
        record = self.db.query(EquipmentResource).filter(EquipmentResource.resource_id == resource_id).first()
        return record.to_domain() if record else None

    def save(self, record_id: str, record_payload: dict, decided_by: str, decided_at: str, recommendation_id: str) -> None:
        existing = self.db.query(DBEvidenceRecord).filter(DBEvidenceRecord.record_id == record_id).first()
        if existing:
            existing.raw_data = record_payload
            existing.decided_by = decided_by
            existing.decided_at = decided_at
        else:
            db_record = DBEvidenceRecord(
                record_id=record_id,
                recommendation_id=recommendation_id,
                decided_by=decided_by,
                decided_at=decided_at,
                raw_data=record_payload
            )
            self.db.add(db_record)
        self.db.commit()

    def get(self, record_id: str) -> Optional[dict]:
        record = self.db.query(DBEvidenceRecord).filter(DBEvidenceRecord.record_id == record_id).first()
        return record.raw_data if record else None
