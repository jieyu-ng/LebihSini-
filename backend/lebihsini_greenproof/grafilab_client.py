"""Real Grafilab text client using the official OpenAI-compatible sample."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    RateLimitError,
)

from lebihsini_greenproof.ai_provider import AIProvider, AIProviderException, AIProviderResponse
from lebihsini_greenproof.contracts import (
    AIExtractionRequest,
    AIProviderError,
    InputSourceType,
    ProviderStatus,
    ResourceKind,
)


DEFAULT_GRAFILAB_BASE_URL = "https://console-api.grafilab.ai/api/oai/v1"
DEFAULT_GRAFILAB_TEXT_MODEL = "grafilab/qwen3.6-flash"
DEFAULT_GRAFILAB_TIMEOUT_SECONDS = 15.0
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


class GrafilabClient(AIProvider):
    provider_name = "grafilab"

    def __init__(
        self,
        api_key_env_var: str = "GRAFILAB_API_KEY",
        *,
        base_url: str | None = None,
        text_model: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self.api_key_env_var = api_key_env_var
        self.api_key = os.getenv(api_key_env_var)
        self.base_url = base_url or os.getenv("GRAFILAB_BASE_URL", DEFAULT_GRAFILAB_BASE_URL)
        self.text_model = text_model or os.getenv("GRAFILAB_TEXT_MODEL", DEFAULT_GRAFILAB_TEXT_MODEL)
        timeout_value = timeout_seconds
        if timeout_value is None:
            timeout_value = float(os.getenv("GRAFILAB_TIMEOUT_SECONDS", str(DEFAULT_GRAFILAB_TIMEOUT_SECONDS)))
        self.timeout_seconds = float(timeout_value)

    def extract_demand(self, request: AIExtractionRequest) -> AIProviderResponse:
        operation_type = self._resolve_demand_operation_type(request)
        response_text = self._run_text_completion(
            system_prompt=self._load_prompt("demand_extraction_v1.txt") + "\n" + self._demand_json_rules(),
            user_payload=self._build_demand_payload(request, operation_type),
            temperature=0.0,
            top_p=0.9,
        )
        payload = self._parse_json_response(response_text)
        if not isinstance(payload.get("fields"), dict):
            raise self._provider_error(
                "INVALID_PROVIDER_OUTPUT",
                "Grafilab demand extraction did not return the expected `fields` object.",
                retryable=False,
            )
        return AIProviderResponse(
            payload={
                "status": ProviderStatus.SUCCESS.value,
                "provider_name": self.provider_name,
                "model_name": self.text_model,
                "model_version": "chat.completions.create",
                "request_id": request.request_id,
                "provider_language": payload.get("provider_language") or request.input_language or "unknown",
                "operation_type": operation_type,
                **payload,
            }
        )

    def extract_resource_scan(
        self,
        request: AIExtractionRequest,
        resource_kind: ResourceKind,
    ) -> AIProviderResponse:
        operation_type = self._resolve_resource_operation_type(request)
        prompt_name = "material_passport_extraction_v1.txt" if resource_kind == ResourceKind.MATERIAL else "equipment_passport_extraction_v1.txt"
        system_prompt = self._load_prompt(prompt_name) + "\n" + self._resource_json_rules(resource_kind)
        response_text = self._run_text_completion(
            system_prompt=system_prompt,
            user_payload=self._build_resource_payload(request, resource_kind, operation_type),
            temperature=0.0,
            top_p=0.9,
        )
        payload = self._parse_json_response(response_text)
        if not isinstance(payload.get("fields"), dict):
            raise self._provider_error(
                "INVALID_PROVIDER_OUTPUT",
                "Grafilab resource structuring did not return the expected `fields` object.",
                retryable=False,
            )
        return AIProviderResponse(
            payload={
                "status": ProviderStatus.SUCCESS.value,
                "provider_name": self.provider_name,
                "model_name": self.text_model,
                "model_version": "chat.completions.create",
                "request_id": request.request_id,
                "provider_language": payload.get("provider_language") or request.input_language or "unknown",
                "operation_type": operation_type,
                **payload,
            }
        )

    def explain(self, prompt_name: str, payload: dict) -> AIProviderResponse:
        response_text = self._run_text_completion(
            system_prompt=self._build_explanation_prompt(prompt_name),
            user_payload=json.dumps(payload, indent=2, sort_keys=True),
            temperature=0.1,
            top_p=0.9,
        )
        return AIProviderResponse(
            payload={
                "status": ProviderStatus.SUCCESS.value,
                "provider_name": self.provider_name,
                "model_name": self.text_model,
                "model_version": "chat.completions.create",
                "request_id": str(payload.get("request_id", "grafilab-explanation")),
                "operation_type": "plain_language_explanation",
                "text": response_text.strip(),
            }
        )

    def _create_client(self) -> OpenAI:
        if not self.api_key:
            raise self._provider_error(
                "AI_PROVIDER_UNAVAILABLE",
                f"Real Grafilab mode requires the `{self.api_key_env_var}` environment variable.",
                retryable=False,
            )
        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout_seconds,
        )

    def _run_text_completion(
        self,
        *,
        system_prompt: str,
        user_payload: str,
        temperature: float,
        top_p: float,
    ) -> str:
        client = self._create_client()
        try:
            response = client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_payload},
                ],
                temperature=temperature,
                top_p=top_p,
            )
        except AuthenticationError as exc:
            raise self._provider_error(
                "AI_PROVIDER_UNAVAILABLE",
                "Grafilab authentication failed. Check the configured API key.",
                retryable=False,
            ) from exc
        except RateLimitError as exc:
            raise self._provider_error(
                "AI_PROVIDER_UNAVAILABLE",
                "Grafilab rate limiting prevented the request from completing.",
                retryable=True,
            ) from exc
        except (APITimeoutError, APIConnectionError) as exc:
            raise self._provider_error(
                "AI_PROVIDER_UNAVAILABLE",
                "Grafilab did not respond before the configured timeout.",
                retryable=True,
            ) from exc
        except BadRequestError as exc:
            raise self._provider_error(
                "INVALID_PROVIDER_OUTPUT",
                "Grafilab rejected the request payload.",
                retryable=False,
            ) from exc
        except APIError as exc:
            raise self._provider_error(
                "AI_PROVIDER_UNAVAILABLE",
                "Grafilab returned an unexpected provider error.",
                retryable=True,
            ) from exc

        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise self._provider_error(
                "INVALID_PROVIDER_OUTPUT",
                "Grafilab returned no message content.",
                retryable=False,
            ) from exc
        if content is None or not str(content).strip():
            raise self._provider_error(
                "INVALID_PROVIDER_OUTPUT",
                "Grafilab returned an empty response body.",
                retryable=False,
            )
        return str(content)

    def _parse_json_response(self, response_text: str) -> dict[str, Any]:
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise self._provider_error(
                "INVALID_PROVIDER_OUTPUT",
                "Grafilab returned malformed JSON.",
                retryable=False,
            ) from exc
        if not isinstance(parsed, dict):
            raise self._provider_error(
                "INVALID_PROVIDER_OUTPUT",
                "Grafilab returned JSON in an unsupported top-level shape.",
                retryable=False,
            )
        return parsed

    def _resolve_demand_operation_type(self, request: AIExtractionRequest) -> str:
        if request.source_type == InputSourceType.TYPED_TEXT:
            return "typed_text_extraction"
        if request.source_type == InputSourceType.VOICE_NOTE:
            if request.content_reference.startswith("audio://"):
                raise self._provider_error(
                    "UNSUPPORTED_INPUT_TYPE",
                    "Real Grafilab mode does not yet support raw audio transcription.",
                    retryable=False,
                )
            return "transcript_text_extraction"
        if request.source_type in {
            InputSourceType.HANDWRITTEN_LIST,
            InputSourceType.QUOTATION_DOCUMENT,
        }:
            return "ocr_text_extraction"
        raise self._provider_error(
            "UNSUPPORTED_INPUT_TYPE",
            f"Real Grafilab mode does not yet support raw `{request.source_type.value}` extraction.",
            retryable=False,
        )

    def _resolve_resource_operation_type(self, request: AIExtractionRequest) -> str:
        if request.source_type in {
            InputSourceType.TYPED_TEXT,
            InputSourceType.HANDWRITTEN_LIST,
            InputSourceType.QUOTATION_DOCUMENT,
        }:
            return "ocr_text_extraction"
        raise self._provider_error(
            "UNSUPPORTED_INPUT_TYPE",
            f"Real Grafilab mode does not yet support raw `{request.source_type.value}` resource extraction.",
            retryable=False,
        )

    def _build_demand_payload(self, request: AIExtractionRequest, operation_type: str) -> str:
        return json.dumps(
            {
                "request_id": request.request_id,
                "operation_type": operation_type,
                "source_type": request.source_type.value,
                "input_language": request.input_language,
                "reference_datetime": request.reference_datetime,
                "timezone": request.timezone,
                "content": request.content,
            },
            indent=2,
            sort_keys=True,
        )

    def _build_resource_payload(
        self,
        request: AIExtractionRequest,
        resource_kind: ResourceKind,
        operation_type: str,
    ) -> str:
        return json.dumps(
            {
                "request_id": request.request_id,
                "operation_type": operation_type,
                "resource_kind": resource_kind.value,
                "source_type": request.source_type.value,
                "input_language": request.input_language,
                "content": request.content,
            },
            indent=2,
            sort_keys=True,
        )

    def _demand_json_rules(self) -> str:
        return (
            "Return one JSON object with this shape:\n"
            "{\n"
            '  "provider_language": "ms-MY or en-MY or unknown",\n'
            '  "fields": {\n'
            '    "material_category": {"value": string|null, "confidence": number},\n'
            '    "product_code": {"value": string|null, "confidence": number},\n'
            '    "colour": {"value": string|null, "confidence": number},\n'
            '    "dimensions": {"value": string|null, "confidence": number},\n'
            '    "quantity_units": {"value": string|number|null, "confidence": number},\n'
            '    "equipment_category": {"value": string|null, "confidence": number},\n'
            '    "equipment_duration_days": {"value": string|number|null, "confidence": number},\n'
            '    "deadline_relative": {"value": string|null, "confidence": number}\n'
            "  }\n"
            "}\n"
            "Use null for absent evidence, no markdown, no commentary, no cost or carbon arithmetic."
        )

    def _resource_json_rules(self, resource_kind: ResourceKind) -> str:
        if resource_kind == ResourceKind.MATERIAL:
            return (
                "Return one JSON object with this shape:\n"
                "{\n"
                '  "provider_language": "ms-MY or en-MY or unknown",\n'
                '  "fields": {\n'
                '    "material_category": {"value": string|null, "confidence": number},\n'
                '    "brand": {"value": string|null, "confidence": number},\n'
                '    "product_code": {"value": string|null, "confidence": number},\n'
                '    "dimensions": {"value": string|null, "confidence": number},\n'
                '    "colour": {"value": string|null, "confidence": number},\n'
                '    "batch_number": {"value": string|null, "confidence": number},\n'
                '    "quantity_estimate_units": {"value": string|number|null, "confidence": number},\n'
                '    "packaging_status": {"value": string|null, "confidence": number},\n'
                '    "storage_condition": {"value": string|null, "confidence": number},\n'
                '    "available_from_at": {"value": string|null, "confidence": number}\n'
                "  }\n"
                "}\n"
                "Do not invent unreadable labels or invisible evidence."
            )
        return (
            "Return one JSON object with this shape:\n"
            "{\n"
            '  "provider_language": "ms-MY or en-MY or unknown",\n'
            '  "fields": {\n'
            '    "category": {"value": string|null, "confidence": number},\n'
            '    "brand_model": {"value": string|null, "confidence": number},\n'
            '    "capacity": {"value": string|null, "confidence": number},\n'
            '    "maintenance_date_at": {"value": string|null, "confidence": number},\n'
            '    "maintenance_record_present": {"value": boolean|null, "confidence": number},\n'
            '    "operator_required": {"value": boolean|null, "confidence": number},\n'
            '    "visible_condition": {"value": string|null, "confidence": number}\n'
            "  }\n"
            "}\n"
            "Do not certify maintenance, do not invent dates, and use null when evidence is absent."
        )

    def _build_explanation_prompt(self, prompt_name: str) -> str:
        prompt_file = PROMPTS_DIR / f"{prompt_name}.txt"
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8").strip()
        return (
            "Rewrite the supplied recommendation facts into plain language. "
            "Do not change quantities, costs, carbon totals, exclusions, or approval status."
        )

    def _load_prompt(self, filename: str) -> str:
        return (PROMPTS_DIR / filename).read_text(encoding="utf-8").strip()

    def _provider_error(self, code: str, message: str, *, retryable: bool) -> AIProviderException:
        return AIProviderException(
            AIProviderError(
                code=code,
                message=message,
                retryable=retryable,
                provider_name=self.provider_name,
            )
        )
