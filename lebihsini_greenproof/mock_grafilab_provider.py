from __future__ import annotations

from lebihsini_greenproof.ai_demo_fixtures import MOCK_DEMAND_FIXTURES, MOCK_RESOURCE_FIXTURES
from lebihsini_greenproof.ai_provider import AIProvider, AIProviderException, AIProviderResponse
from lebihsini_greenproof.contracts import (
    AIExtractionRequest,
    AIProviderError,
    ProviderStatus,
    ResourceKind,
)


class MockGrafilabProvider(AIProvider):
    provider_name = "mock_grafilab"

    def extract_demand(self, request: AIExtractionRequest) -> AIProviderResponse:
        payload = MOCK_DEMAND_FIXTURES.get(request.content_reference)
        if payload is None:
            raise AIProviderException(
                AIProviderError(
                    code="INPUT_UNREADABLE",
                    message="No deterministic demand fixture exists for this input reference.",
                    retryable=False,
                    provider_name=self.provider_name,
                )
            )
        return AIProviderResponse(
            payload={
                "status": ProviderStatus.SUCCESS.value,
                "provider_name": self.provider_name,
                "model_name": "mock-demand-extractor",
                "model_version": "v1",
                "request_id": request.request_id,
                **payload,
            }
        )

    def extract_resource_scan(
        self,
        request: AIExtractionRequest,
        resource_kind: ResourceKind,
    ) -> AIProviderResponse:
        payload = MOCK_RESOURCE_FIXTURES.get(request.content_reference)
        if payload is None or payload.get("resource_kind") != resource_kind.value:
            raise AIProviderException(
                AIProviderError(
                    code="INPUT_UNREADABLE",
                    message="No deterministic resource fixture exists for this input reference.",
                    retryable=False,
                    provider_name=self.provider_name,
                )
            )
        return AIProviderResponse(
            payload={
                "status": ProviderStatus.SUCCESS.value,
                "provider_name": self.provider_name,
                "model_name": "mock-resource-extractor",
                "model_version": "v1",
                "request_id": request.request_id,
                **payload,
            }
        )

    def explain(self, prompt_name: str, payload: dict) -> AIProviderResponse:
        return AIProviderResponse(
            payload={
                "status": ProviderStatus.SUCCESS.value,
                "provider_name": self.provider_name,
                "model_name": "mock-explainer",
                "model_version": "v1",
                "request_id": payload.get("request_id", "mock-explanation"),
                "text": f"Mock explanation generated for {prompt_name}.",
            }
        )
