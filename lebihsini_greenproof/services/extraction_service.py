from __future__ import annotations

from dataclasses import replace

from lebihsini_greenproof.ai_extraction import (
    ConfirmationInput,
    confirm_demand_extraction,
    extract_demand,
    generate_passport_from_resource_scan,
)
from lebihsini_greenproof.ai_provider import AIProvider, AIProviderException
from lebihsini_greenproof.contracts import (
    AIExtractionRequest,
    ConfirmationAction,
    EquipmentResourcePassport,
    MaterialResourcePassport,
    PassportGenerationResult,
    ResourceKind,
    StructuredDemandExtractionResult,
    UserConfirmedExtraction,
)
from lebihsini_greenproof.demo_data import DemoDataset
from lebihsini_greenproof.repositories.in_memory import InMemoryRepository, StoredExtraction


class ServiceError(RuntimeError):
    def __init__(self, code: str, message: str, *, status_code: int, details: dict | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def _map_provider_error(exc: AIProviderException) -> ServiceError:
    status_code = 503 if exc.error.code == "AI_PROVIDER_UNAVAILABLE" else 400
    return ServiceError(
        exc.error.code,
        exc.error.message,
        status_code=status_code,
        details={"provider_name": exc.error.provider_name, "retryable": exc.error.retryable},
    )


class ExtractionService:
    def __init__(
        self,
        repository: InMemoryRepository,
        dataset: DemoDataset,
        provider: AIProvider,
    ) -> None:
        self.repository = repository
        self.dataset = dataset
        self.provider = provider

    def create_extraction(self, request: AIExtractionRequest) -> tuple[str, StructuredDemandExtractionResult]:
        try:
            result = extract_demand(request, self.provider)
        except AIProviderException as exc:
            raise _map_provider_error(exc) from exc
        except ValueError as exc:
            raise ServiceError("INVALID_PROVIDER_OUTPUT", str(exc), status_code=502) from exc
        extraction_id = self.repository.next_extraction_id()
        self.repository.extractions[extraction_id] = StoredExtraction(
            extraction_id=extraction_id,
            request=request,
            extraction=result,
        )
        return extraction_id, result

    def confirm_extraction(
        self,
        extraction_id: str,
        action: ConfirmationAction,
        confirmed_values: dict[str, object],
        confirmed_at: str,
    ) -> tuple[str, UserConfirmedExtraction]:
        stored = self.repository.extractions.get(extraction_id)
        if stored is None:
            raise ServiceError("RESOURCE_NOT_FOUND", "Extraction was not found.", status_code=404)
        confirmation = confirm_demand_extraction(
            stored.extraction,
            ConfirmationInput(
                request_id=stored.request.request_id,
                action=action,
                confirmed_values=confirmed_values,
                confirmed_at=confirmed_at,
            ),
        )
        blocking_actions = {
            ConfirmationAction.ACCEPT,
            ConfirmationAction.EDIT,
            ConfirmationAction.PROVIDE,
        }
        if action in blocking_actions and confirmation.confirmed_demand is None:
            raise ServiceError(
                "MISSING_CRITICAL_FIELD",
                "Quantity, deadline, and other critical fields must be confirmed before generating a recommendation.",
                status_code=409,
                details={"warnings": [warning.field_name for warning in confirmation.warnings]},
            )
        confirmation_id = self.repository.next_confirmation_id()
        self.repository.confirmations[confirmation_id] = confirmation
        if confirmation.confirmed_demand is not None:
            self.repository.confirmation_demands[confirmation_id] = confirmation.confirmed_demand
        return confirmation_id, confirmation

    def create_material_passport(
        self,
        request: AIExtractionRequest,
        resource_id: str,
        human_confirmed_quantity_units: int | None = None,
    ) -> PassportGenerationResult:
        base_passport = self._get_material_passport(resource_id)
        try:
            _, result = generate_passport_from_resource_scan(
                request,
                self.provider,
                ResourceKind.MATERIAL,
                base_passport,
            )
        except AIProviderException as exc:
            raise _map_provider_error(exc) from exc
        except ValueError as exc:
            raise ServiceError("INVALID_PROVIDER_OUTPUT", str(exc), status_code=502) from exc
        if human_confirmed_quantity_units is not None and result.generated_material_passport is not None:
            result = replace(
                result,
                generated_material_passport=replace(
                    result.generated_material_passport,
                    human_confirmed_quantity_units=human_confirmed_quantity_units,
                ),
            )
        if result.generated_material_passport is not None:
            self.repository.material_passports[result.generated_material_passport.resource_id] = result.generated_material_passport
        return result

    def create_equipment_passport(
        self,
        request: AIExtractionRequest,
        resource_id: str,
        base_override: EquipmentResourcePassport | None = None,
    ) -> PassportGenerationResult:
        base_passport = base_override or self._get_equipment_passport(resource_id)
        try:
            _, result = generate_passport_from_resource_scan(
                request,
                self.provider,
                ResourceKind.EQUIPMENT,
                base_passport,
            )
        except AIProviderException as exc:
            raise _map_provider_error(exc) from exc
        except ValueError as exc:
            raise ServiceError("INVALID_PROVIDER_OUTPUT", str(exc), status_code=502) from exc
        if result.generated_equipment_passport is not None:
            self.repository.equipment_passports[result.generated_equipment_passport.resource_id] = result.generated_equipment_passport
        return result

    def _get_material_passport(self, resource_id: str) -> MaterialResourcePassport:
        for resource in self.dataset.material_resources:
            if resource.resource_id == resource_id:
                return resource
        raise ServiceError("RESOURCE_NOT_FOUND", "Material resource was not found.", status_code=404)

    def _get_equipment_passport(self, resource_id: str) -> EquipmentResourcePassport:
        if self.dataset.commercial_equipment_fallback.resource_id == resource_id:
            return self.dataset.commercial_equipment_fallback
        for resource in self.dataset.equipment_resources:
            if resource.resource_id == resource_id:
                return resource
        raise ServiceError("RESOURCE_NOT_FOUND", "Equipment resource was not found.", status_code=404)
