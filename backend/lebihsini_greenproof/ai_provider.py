"""Provider boundary for AI extraction.

The application depends on this interface, not on Grafilab-specific response
shapes. Offline tests use the mock provider only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from lebihsini_greenproof.contracts import AIExtractionRequest, AIProviderError, ResourceKind


@dataclass(slots=True)
class AIProviderResponse:
    payload: dict


class AIProvider(Protocol):
    provider_name: str

    def extract_demand(self, request: AIExtractionRequest) -> AIProviderResponse:
        ...

    def extract_resource_scan(
        self,
        request: AIExtractionRequest,
        resource_kind: ResourceKind,
    ) -> AIProviderResponse:
        ...

    def explain(self, prompt_name: str, payload: dict) -> AIProviderResponse:
        ...


class AIProviderException(RuntimeError):
    def __init__(self, error: AIProviderError) -> None:
        super().__init__(error.message)
        self.error = error
