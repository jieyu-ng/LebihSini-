from __future__ import annotations

from lebihsini_greenproof.contracts import InputSourceType


def normalize_language_code(value: str | None) -> str:
    if not value:
        return "unknown"
    lowered = value.lower()
    mapping = {
        "ms": "ms-MY",
        "ms-my": "ms-MY",
        "bahasa malaysia": "ms-MY",
        "bm": "ms-MY",
        "en": "en-MY",
        "en-my": "en-MY",
        "english": "en-MY",
    }
    return mapping.get(lowered, value)


def normalize_input_source_type(value: str) -> InputSourceType:
    return InputSourceType(value)
