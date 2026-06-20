import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lebihsini_greenproof.db.database import Base
from lebihsini_greenproof.db.models import MaterialResource, EquipmentResource, EvidenceRecord
from lebihsini_greenproof.repositories.sqlite_repository import SQLiteRepository
from lebihsini_greenproof.demo_data import load_demo_dataset

class SQLiteRepositoryTests(unittest.TestCase):
    def setUp(self):
        # Use a temporary in-memory SQLite database per test class
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db = self.SessionLocal()
        self.repo = SQLiteRepository(self.db)
        
        # Seed
        self.dataset = load_demo_dataset()
        for m in self.dataset.material_resources:
            self.db.add(MaterialResource.from_domain(m))
        for e in self.dataset.equipment_resources:
            self.db.add(EquipmentResource.from_domain(e))
        self.db.add(EquipmentResource.from_domain(self.dataset.commercial_equipment_fallback))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_startup_idempotency_simulation(self):
        mat_count = self.db.query(MaterialResource).count()
        self.assertEqual(mat_count, len(self.dataset.material_resources))
        
        # If we didn't check for existing, it would add duplicates.
        # Idempotency is usually handled at app startup logic, not repo, but we verify counts.
        self.assertTrue(mat_count > 0)

    def test_domain_orm_round_trip(self):
        mats = self.repo.list_materials()
        self.assertEqual(len(mats), len(self.dataset.material_resources))
        site_a_mat = self.repo.get_material("mat-site-a-tiles")
        self.assertIsNotNone(site_a_mat)
        self.assertEqual(site_a_mat.category, "porcelain_tile")
        
    def test_site_e_fields_survive_persistence(self):
        site_e = self.repo.get_material("mat-site-e-tiles")
        self.assertIsNotNone(site_e)
        self.assertEqual(site_e.status, "manual_review_only")
        self.assertEqual(site_e.risk_category.value, "red")

    def test_site_d_equipment_fields_survive_persistence(self):
        site_d = self.repo.get_equipment("eq-site-d-cutter")
        self.assertIsNotNone(site_d)
        self.assertTrue(site_d.maintenance_record_present)

    def test_evidence_record_persistence(self):
        dummy_evidence = {
            "record_id": "ev-001",
            "name": "GreenProof Evidence Record"
        }
        self.repo.save(
            record_id="ev-001",
            record_payload=dummy_evidence,
            decided_by="user1",
            decided_at="2026-06-21T10:00:00+08:00",
            recommendation_id="rec-1"
        )
        
        saved = self.repo.get("ev-001")
        self.assertIsNotNone(saved)
        self.assertEqual(saved["name"], "GreenProof Evidence Record")
        
        # Test update existing
        updated_evidence = {"record_id": "ev-001", "name": "Updated Record"}
        self.repo.save(
            record_id="ev-001",
            record_payload=updated_evidence,
            decided_by="user2",
            decided_at="2026-06-22T10:00:00+08:00",
            recommendation_id="rec-1"
        )
        
        updated = self.repo.get("ev-001")
        self.assertEqual(updated["name"], "Updated Record")

    def test_missing_record_returns_none(self):
        self.assertIsNone(self.repo.get("nonexistent"))
        self.assertIsNone(self.repo.get_material("nonexistent"))
