"""Grafilab provider skeleton.

Official Grafilab endpoint URLs, authentication headers, and SDK details were
not present in this repository during implementation. This module therefore
provides only a production-client skeleton and intentionally avoids inventing
network behavior.
"""

from __future__ import annotations

import os

from lebihsini_greenproof.ai_provider import AIProvider, AIProviderResponse
from lebihsini_greenproof.contracts import AIExtractionRequest, ResourceKind


class GrafilabClient(AIProvider):
    provider_name = "grafilab"

    def __init__(self, api_key_env_var: str = "GRAFILAB_API_KEY", timeout_seconds: float = 15.0) -> None:
        self.api_key_env_var = api_key_env_var
        self.timeout_seconds = timeout_seconds
        self.api_key = os.getenv(api_key_env_var)

    def extract_demand(self, request: AIExtractionRequest) -> AIProviderResponse:
        del request
        raise NotImplementedError(
            "Official Grafilab demand-extraction API details are not available in this repository."
        )

    def extract_resource_scan(
        self,
        request: AIExtractionRequest,
        resource_kind: ResourceKind,
    ) -> AIProviderResponse:
        del request, resource_kind
        raise NotImplementedError(
            "Official Grafilab resource-scan API details are not available in this repository."
        )

    def explain(self, prompt_name: str, payload: dict) -> AIProviderResponse:
        del prompt_name, payload
        raise NotImplementedError(
            "Official Grafilab explanation API details are not available in this repository."
        )
