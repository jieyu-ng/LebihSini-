import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from openai import APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError

from lebihsini_greenproof.ai_extraction import ConfirmationInput, confirm_demand_extraction, extract_demand
from lebihsini_greenproof.ai_provider import AIProviderException
from lebihsini_greenproof.contracts import AIExtractionRequest, ConfirmationAction, InputSourceType, ResourceKind
from lebihsini_greenproof.grafilab_client import (
    DEFAULT_GRAFILAB_BASE_URL,
    DEFAULT_GRAFILAB_TEXT_MODEL,
    GrafilabClient,
)
from lebihsini_greenproof.mock_grafilab_provider import MockGrafilabProvider


class FakeChatCompletions:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response


class FakeOpenAIClient:
    def __init__(self, completions):
        self.chat = SimpleNamespace(completions=completions)


def _fake_response(content: str):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content),
            )
        ]
    )


class GrafilabClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = AIExtractionRequest(
            request_id="real-001",
            source_type=InputSourceType.TYPED_TEXT,
            content="Need 500 grey porcelain tiles 600x600 and one tile cutter for two days by tomorrow 11:00.",
            content_reference="text://typed/en/request-001",
            input_language="en-MY",
            reference_datetime="2026-06-20T09:00:00+08:00",
        )

    def test_official_default_base_url_and_model(self) -> None:
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": ""}, clear=False):
            client = GrafilabClient()
        self.assertEqual(client.base_url, DEFAULT_GRAFILAB_BASE_URL)
        self.assertEqual(client.text_model, DEFAULT_GRAFILAB_TEXT_MODEL)

    def test_api_key_loaded_from_environment(self) -> None:
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        self.assertEqual(client.api_key, "secret-key")

    def test_missing_api_key_blocks_real_mode(self) -> None:
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": ""}, clear=False):
            client = GrafilabClient()
            with self.assertRaises(AIProviderException) as ctx:
                client._create_client()
        self.assertEqual(ctx.exception.error.code, "AI_PROVIDER_UNAVAILABLE")

    def test_chat_completions_create_invocation(self) -> None:
        completions = FakeChatCompletions(
            response=_fake_response(
                '{"provider_language":"en-MY","fields":{"material_category":{"value":"porcelain_tile","confidence":0.9},"product_code":{"value":"PG-600-GREY","confidence":0.8},"colour":{"value":"grey","confidence":0.9},"dimensions":{"value":"600x600","confidence":0.9},"quantity_units":{"value":500,"confidence":0.9},"equipment_category":{"value":"tile_cutter","confidence":0.9},"equipment_duration_days":{"value":2,"confidence":0.9},"deadline_relative":{"value":"tomorrow 11:00","confidence":0.9}}}'
            )
        )
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with patch.object(client, "_create_client", return_value=FakeOpenAIClient(completions)):
            extract_demand(self.request, client)
        self.assertEqual(completions.calls[0]["model"], DEFAULT_GRAFILAB_TEXT_MODEL)
        self.assertEqual(completions.calls[0]["temperature"], 0.0)
        self.assertEqual(completions.calls[0]["top_p"], 0.9)

    def test_bahasa_typed_extraction(self) -> None:
        request = AIExtractionRequest(
            request_id="bm-typed-001",
            source_type=InputSourceType.TYPED_TEXT,
            content="Esok perlukan 500 tile kelabu 600 kali 600 dan mesin pemotong untuk dua hari.",
            content_reference="text://typed/ms/request-001",
            input_language="ms-MY",
            reference_datetime="2026-06-20T09:00:00+08:00",
        )
        completions = FakeChatCompletions(
            response=_fake_response(
                '{"provider_language":"ms-MY","fields":{"material_category":{"value":"porcelain_tile","confidence":0.9},"product_code":{"value":"PG-600-GREY","confidence":0.6},"colour":{"value":"grey","confidence":0.9},"dimensions":{"value":"600x600","confidence":0.9},"quantity_units":{"value":"500","confidence":0.9},"equipment_category":{"value":"tile_cutter","confidence":0.9},"equipment_duration_days":{"value":"2","confidence":0.9},"deadline_relative":{"value":"esok","confidence":0.8}}}'
            )
        )
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with patch.object(client, "_create_client", return_value=FakeOpenAIClient(completions)):
            result = extract_demand(request, client)
        self.assertEqual(result.detected_language, "ms-MY")
        self.assertEqual(result.normalized_demand["quantity_units"], 500)

    def test_transcript_text_extraction_is_labelled_honestly(self) -> None:
        request = AIExtractionRequest(
            request_id="voice-transcript-001",
            source_type=InputSourceType.VOICE_NOTE,
            content="Esok perlukan 500 tile kelabu 600 kali 600 dan mesin pemotong untuk dua hari.",
            content_reference="transcript://voice-note/request-001",
            input_language="ms-MY",
            reference_datetime="2026-06-20T09:00:00+08:00",
        )
        completions = FakeChatCompletions(
            response=_fake_response(
                '{"provider_language":"ms-MY","fields":{"material_category":{"value":"porcelain_tile","confidence":0.9},"product_code":{"value":"PG-600-GREY","confidence":0.6},"colour":{"value":"grey","confidence":0.9},"dimensions":{"value":"600x600","confidence":0.9},"quantity_units":{"value":"500","confidence":0.9},"equipment_category":{"value":"tile_cutter","confidence":0.9},"equipment_duration_days":{"value":"2","confidence":0.9},"deadline_relative":{"value":"esok","confidence":0.8}}}'
            )
        )
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with patch.object(client, "_create_client", return_value=FakeOpenAIClient(completions)):
            result = extract_demand(request, client)
        self.assertEqual(result.model_metadata.operation_type, "transcript_text_extraction")

    def test_json_code_fence_cleanup(self) -> None:
        completions = FakeChatCompletions(
            response=_fake_response(
                "```json\n{\"provider_language\":\"en-MY\",\"fields\":{\"material_category\":{\"value\":\"porcelain_tile\",\"confidence\":0.9},\"product_code\":{\"value\":\"PG-600-GREY\",\"confidence\":0.8},\"colour\":{\"value\":\"grey\",\"confidence\":0.9},\"dimensions\":{\"value\":\"600x600\",\"confidence\":0.9},\"quantity_units\":{\"value\":500,\"confidence\":0.9},\"equipment_category\":{\"value\":\"tile_cutter\",\"confidence\":0.9},\"equipment_duration_days\":{\"value\":2,\"confidence\":0.9},\"deadline_relative\":{\"value\":\"tomorrow 11:00\",\"confidence\":0.9}}}\n```"
            )
        )
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with patch.object(client, "_create_client", return_value=FakeOpenAIClient(completions)):
            result = extract_demand(self.request, client)
        self.assertEqual(result.normalized_demand["dimension_mm_width"], 600)

    def test_malformed_json_becomes_provider_error(self) -> None:
        completions = FakeChatCompletions(response=_fake_response("{not valid json"))
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with patch.object(client, "_create_client", return_value=FakeOpenAIClient(completions)):
            with self.assertRaises(AIProviderException) as ctx:
                client.extract_demand(self.request)
        self.assertEqual(ctx.exception.error.code, "INVALID_PROVIDER_OUTPUT")

    def test_empty_response_becomes_provider_error(self) -> None:
        completions = FakeChatCompletions(response=_fake_response("   "))
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with patch.object(client, "_create_client", return_value=FakeOpenAIClient(completions)):
            with self.assertRaises(AIProviderException):
                client.extract_demand(self.request)

    def test_missing_choices_becomes_provider_error(self) -> None:
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with patch.object(client, "_create_client", return_value=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **_: SimpleNamespace(choices=[]))))):
            with self.assertRaises(AIProviderException):
                client.extract_demand(self.request)

    def test_authentication_failure_is_mapped(self) -> None:
        request = httpx.Request("POST", "https://console-api.grafilab.ai/api/oai/v1/chat/completions")
        response = httpx.Response(401, request=request)
        completions = FakeChatCompletions(
            error=AuthenticationError("auth failed", response=response, body={}),
        )
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with patch.object(client, "_create_client", return_value=FakeOpenAIClient(completions)):
            with self.assertRaises(AIProviderException) as ctx:
                client.extract_demand(self.request)
        self.assertEqual(ctx.exception.error.code, "AI_PROVIDER_UNAVAILABLE")

    def test_timeout_failure_is_mapped(self) -> None:
        request = httpx.Request("POST", "https://console-api.grafilab.ai/api/oai/v1/chat/completions")
        completions = FakeChatCompletions(error=APITimeoutError(request=request))
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with patch.object(client, "_create_client", return_value=FakeOpenAIClient(completions)):
            with self.assertRaises(AIProviderException) as ctx:
                client.extract_demand(self.request)
        self.assertEqual(ctx.exception.error.code, "AI_PROVIDER_UNAVAILABLE")

    def test_rate_limit_failure_is_mapped(self) -> None:
        request = httpx.Request("POST", "https://console-api.grafilab.ai/api/oai/v1/chat/completions")
        response = httpx.Response(429, request=request)
        completions = FakeChatCompletions(
            error=RateLimitError("rate limited", response=response, body={}),
        )
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with patch.object(client, "_create_client", return_value=FakeOpenAIClient(completions)):
            with self.assertRaises(AIProviderException) as ctx:
                client.extract_demand(self.request)
        self.assertEqual(ctx.exception.error.code, "AI_PROVIDER_UNAVAILABLE")

    def test_connection_failure_is_mapped(self) -> None:
        request = httpx.Request("POST", "https://console-api.grafilab.ai/api/oai/v1/chat/completions")
        completions = FakeChatCompletions(error=APIConnectionError(request=request))
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with patch.object(client, "_create_client", return_value=FakeOpenAIClient(completions)):
            with self.assertRaises(AIProviderException) as ctx:
                client.extract_demand(self.request)
        self.assertEqual(ctx.exception.error.code, "AI_PROVIDER_UNAVAILABLE")

    def test_unsupported_raw_image_is_blocked(self) -> None:
        request = AIExtractionRequest(
            request_id="img-001",
            source_type=InputSourceType.IMAGE,
            content="raw image placeholder",
            content_reference="image://raw",
            input_language="en-MY",
        )
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with self.assertRaises(AIProviderException) as ctx:
            client.extract_demand(request)
        self.assertEqual(ctx.exception.error.code, "UNSUPPORTED_INPUT_TYPE")

    def test_unsupported_raw_audio_is_blocked(self) -> None:
        request = AIExtractionRequest(
            request_id="audio-001",
            source_type=InputSourceType.VOICE_NOTE,
            content="",
            content_reference="audio://raw",
            input_language="en-MY",
        )
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with self.assertRaises(AIProviderException) as ctx:
            client.extract_demand(request)
        self.assertEqual(ctx.exception.error.code, "UNSUPPORTED_INPUT_TYPE")

    def test_unsupported_raw_image_resource_scan_is_blocked(self) -> None:
        request = AIExtractionRequest(
            request_id="photo-001",
            source_type=InputSourceType.RESOURCE_PHOTO,
            content="raw photo placeholder",
            content_reference="resource://raw",
            input_language="en-MY",
        )
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with self.assertRaises(AIProviderException) as ctx:
            client.extract_resource_scan(request, resource_kind=ResourceKind.MATERIAL)
        self.assertEqual(ctx.exception.error.code, "UNSUPPORTED_INPUT_TYPE")

    def test_confirmation_boundary_preserved(self) -> None:
        completions = FakeChatCompletions(
            response=_fake_response(
                '{"provider_language":"en-MY","fields":{"material_category":{"value":"porcelain_tile","confidence":0.9},"product_code":{"value":"PG-600-GREY","confidence":0.8},"colour":{"value":"grey","confidence":0.9},"dimensions":{"value":"600x600","confidence":0.9},"quantity_units":{"value":500,"confidence":0.9},"equipment_category":{"value":"tile_cutter","confidence":0.9},"equipment_duration_days":{"value":2,"confidence":0.9},"deadline_relative":{"value":"tomorrow 11:00","confidence":0.9}}}'
            )
        )
        with patch.dict(os.environ, {"GRAFILAB_API_KEY": "secret-key"}, clear=False):
            client = GrafilabClient()
        with patch.object(client, "_create_client", return_value=FakeOpenAIClient(completions)):
            extraction = extract_demand(self.request, client)
        confirmed = confirm_demand_extraction(
            extraction,
            ConfirmationInput(
                request_id=self.request.request_id,
                action=ConfirmationAction.ACCEPT,
                confirmed_values={"product_code": "PG-600-GREY"},
                confirmed_at="2026-06-20T09:05:00+08:00",
            ),
        )
        self.assertIsNotNone(confirmed.confirmed_demand)

    def test_mock_provider_remains_unchanged(self) -> None:
        provider = MockGrafilabProvider()
        result = extract_demand(
            AIExtractionRequest(
                request_id="mock-001",
                source_type=InputSourceType.TYPED_TEXT,
                content="Need 500 grey porcelain tiles 600x600 and one tile cutter for two days by tomorrow 11:00.",
                content_reference="demo://typed/en/request-001",
                input_language="en-MY",
                reference_datetime="2026-06-20T09:00:00+08:00",
            ),
            provider,
        )
        self.assertEqual(result.detected_language, "en-MY")


if __name__ == "__main__":
    unittest.main()
