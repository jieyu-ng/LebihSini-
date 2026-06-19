from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any


def to_jsonable(value: Any) -> Any:
    """Convert supported Python objects into JSON-compatible structures."""
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    return value


def to_json_text(value: Any) -> str:
    """Serialize supported objects to deterministic JSON text."""
    return json.dumps(to_jsonable(value), indent=2, sort_keys=True)
