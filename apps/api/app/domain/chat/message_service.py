from __future__ import annotations

from typing import Iterator


class MessageService:
    """Message formatting + streaming chunk helper."""

    def output_contract(self) -> str:
        return "messages persist normalized roles, content, and runtime metadata"

    def chunk_text(self, text: str, chunk_size: int = 28) -> Iterator[str]:
        if chunk_size <= 0:
            chunk_size = 28
        for i in range(0, len(text), chunk_size):
            yield text[i : i + chunk_size]
