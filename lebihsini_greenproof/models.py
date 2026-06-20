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

class EquipmentResource(Base):
    __tablename__ = "equipment_resources"
    resource_id = Column(String, primary_key=True, index=True)
    site_id = Column(String, ForeignKey("projects.project_id"))
    category = Column(String)
    is_commercial_fallback = Column(Boolean, default=False)
    verification_status = Column(String)
    raw_data = Column(JSON)

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
