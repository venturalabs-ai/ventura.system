from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping


@dataclass(frozen=True)
class ContextChunk:
    path: str
    content: str
    score: int


def compile_context(
    task: str,
    files: Mapping[str, str],
    *,
    max_chars: int = 24_000,
) -> list[ContextChunk]:
    """Select relevant repository text without sending the whole repository to an LLM."""
    terms = {t.lower() for t in re.findall(r"[A-Za-z0-9_.-]{3,}", task)}
    ranked: list[ContextChunk] = []
    for path, content in files.items():
        haystack = f"{path}\n{content[:12000]}".lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            ranked.append(ContextChunk(path=path, content=content, score=score))
    ranked.sort(key=lambda item: (item.score, -len(item.content)), reverse=True)

    selected: list[ContextChunk] = []
    used = 0
    for chunk in ranked:
        remaining = max_chars - used
        if remaining <= 0:
            break
        text = chunk.content[:remaining]
        selected.append(ContextChunk(path=chunk.path, content=text, score=chunk.score))
        used += len(text)
    return selected
