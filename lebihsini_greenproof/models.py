from __future__ import annotations

from sqlalchemy import Column, String, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Project(Base):
    __tablename__ = "projects"
    project_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)

class ResourceRequirement(Base):
    __tablename__ = "resource_requirements"
    demand_id = Column(String, primary_key=True, index=True)
    requesting_site_id = Column(String, ForeignKey("projects.project_id"))
    material_category = Column(String)
    product_code = Column(String)
    quantity_units = Column(Integer)
    deadline_at = Column(String)
    status = Column(String, default="pending")
    # Store full JSON to easily construct the DemandRequest dataclass
    raw_data = Column(JSON)

class MaterialResource(Base):
    __tablename__ = "material_resources"
    resource_id = Column(String, primary_key=True, index=True)
    site_id = Column(String, ForeignKey("projects.project_id"))
    category = Column(String)
    quantity_units = Column(Integer)
    risk_category = Column(String)
    verification_status = Column(String)
    raw_data = Column(JSON)

    def to_domain(self):
        from .contracts import MaterialResourcePassport, RiskCategory, VerificationStatus
        data = self.raw_data.copy()
        if isinstance(data.get("risk_category"), str):
            data["risk_category"] = RiskCategory(data["risk_category"])
        if isinstance(data.get("verification_status"), str):
            data["verification_status"] = VerificationStatus(data["verification_status"])
        return MaterialResourcePassport(**data)

    @classmethod
    def from_domain(cls, domain) -> MaterialResource:
        from .serialization import to_jsonable
        return cls(
            resource_id=domain.resource_id,
            site_id=domain.site_id,
            category=domain.category,
            quantity_units=domain.quantity_units,
            risk_category=domain.risk_category.value,
            verification_status=domain.verification_status.value,
            raw_data=to_jsonable(domain)
        )

class EquipmentResource(Base):
    __tablename__ = "equipment_resources"
    resource_id = Column(String, primary_key=True, index=True)
    site_id = Column(String, ForeignKey("projects.project_id"))
    category = Column(String)
    is_commercial_fallback = Column(Boolean, default=False)
    verification_status = Column(String)
    raw_data = Column(JSON)

    def to_domain(self):
        from .contracts import EquipmentResourcePassport, RiskCategory, VerificationStatus
        data = self.raw_data.copy()
        if isinstance(data.get("risk_category"), str):
            data["risk_category"] = RiskCategory(data["risk_category"])
        if isinstance(data.get("verification_status"), str):
            data["verification_status"] = VerificationStatus(data["verification_status"])
        return EquipmentResourcePassport(**data)

    @classmethod
    def from_domain(cls, domain) -> EquipmentResource:
        from .serialization import to_jsonable
        return cls(
            resource_id=domain.resource_id,
            site_id=domain.site_id,
            category=domain.category,
            is_commercial_fallback=domain.is_commercial_fallback,
            verification_status=domain.verification_status.value,
            raw_data=to_jsonable(domain)
        )

class Recommendation(Base):
    __tablename__ = "recommendations"
    recommendation_id = Column(String, primary_key=True, index=True)
    demand_id = Column(String, ForeignKey("resource_requirements.demand_id"))
    verdict = Column(String)
    raw_data = Column(JSON)

class EvidenceRecord(Base):
    __tablename__ = "evidence_records"
    record_id = Column(String, primary_key=True, index=True)
    recommendation_id = Column(String, ForeignKey("recommendations.recommendation_id"))
    decided_by = Column(String)
    decided_at = Column(String)
    raw_data = Column(JSON)

    def to_domain(self):
        from .contracts import EvidenceRecord as DomainEvidenceRecord
        return DomainEvidenceRecord(**self.raw_data)

    @classmethod
    def from_domain(cls, domain) -> EvidenceRecord:
        from .serialization import to_jsonable
        return cls(
            record_id=domain.record_id,
            recommendation_id=domain.recommendation.recommendation_id,
            decided_by=domain.human_decision.decided_by,
            decided_at=domain.human_decision.decided_at,
            raw_data=to_jsonable(domain)
        )
