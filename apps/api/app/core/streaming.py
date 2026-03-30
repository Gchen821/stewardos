"""Streaming helpers for SSE serialization and chunked text emission."""

from __future__ import annotations

import json
from typing import Any


def to_sse(data: dict[str, Any]) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def iter_text_chunks(text: str, chunk_size: int = 24) -> list[str]:
    if chunk_size <= 0:
        return [text]
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
