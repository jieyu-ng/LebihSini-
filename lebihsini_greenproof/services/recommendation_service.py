from __future__ import annotations

from dataclasses import replace

from lebihsini_greenproof.composer import generate_recommendation
from lebihsini_greenproof.contracts import DemandRequest
from lebihsini_greenproof.demo_data import DemoDataset
from lebihsini_greenproof.repositories.in_memory import InMemoryRepository, StoredRecommendation
from lebihsini_greenproof.services.extraction_service import ServiceError
from lebihsini_greenproof.urgency import RecommendationScenario


from lebihsini_greenproof.repositories import WorkflowRepository, ResourceRepository

class RecommendationService:
    def __init__(self, repository: WorkflowRepository, dataset: DemoDataset, resource_repository: ResourceRepository | None = None) -> None:
        self.repository = repository
        self.dataset = dataset
        self.resource_repository = resource_repository

    def create_recommendation(
        self,
        *,
        confirmed_demand_id: str | None = None,
        demand: DemandRequest | None = None,
    ):
        confirmed_demand = demand
        if confirmed_demand is None:
            if confirmed_demand_id is None:
                raise ServiceError(
                    "MISSING_CRITICAL_FIELD",
                    "A confirmed demand reference or confirmed DemandRequest is required.",
                    status_code=400,
                )
            confirmed_demand = self.repository.confirmation_demands.get(confirmed_demand_id)
            if confirmed_demand is None:
                raise ServiceError("RESOURCE_NOT_FOUND", "Confirmed demand was not found.", status_code=404)
        
        # Build the dynamic dataset from the resource repository if available
        working_dataset = self.dataset
        if self.resource_repository is not None:
            working_dataset = replace(
                self.dataset,
                material_resources=self.resource_repository.list_materials(),
                equipment_resources=self.resource_repository.list_equipment()
            )

        recommendation = generate_recommendation(working_dataset, demand=confirmed_demand)
        recommendation_id = self.repository.next_recommendation_id()
        recommendation = replace(recommendation, recommendation_id=recommendation_id)
        self.repository.recommendations[recommendation_id] = StoredRecommendation(
            recommendation_id=recommendation_id,
            demand=confirmed_demand,
            recommendation=recommendation,
            source_confirmation_id=confirmed_demand_id,
        )
        return recommendation

    def recalculate_recommendation(
        self,
        recommendation_id: str,
        scenario: RecommendationScenario,
    ):
        stored = self.repository.recommendations.get(recommendation_id)
        if stored is None:
            raise ServiceError("RECOMMENDATION_NOT_FOUND", "Recommendation was not found.", status_code=404)
            
        working_dataset = self.dataset
        if self.resource_repository is not None:
            working_dataset = replace(
                self.dataset,
                material_resources=self.resource_repository.list_materials(),
                equipment_resources=self.resource_repository.list_equipment()
            )

        recommendation = generate_recommendation(working_dataset, demand=stored.demand, scenario=scenario)
        next_id = self.repository.next_recommendation_id()
        recommendation = replace(recommendation, recommendation_id=next_id)
        self.repository.recommendations[next_id] = StoredRecommendation(
            recommendation_id=next_id,
            demand=replace(stored.demand, deadline_at=scenario.revised_deadline_at or stored.demand.deadline_at),
            recommendation=recommendation,
            source_confirmation_id=stored.source_confirmation_id,
        )
        return recommendation
