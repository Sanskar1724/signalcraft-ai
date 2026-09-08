"""Prompt-leakage sanitizer (§2, §12): internal reasoning, strategy chatter
and mock scaffolding must NEVER reach users. Defense in depth: scrub at every
user-facing boundary AND reject in the validation gate.
"""
from __future__ import annotations

import re

__all__ = ["LEAK_PATTERNS", "leak_found", "scrub"]

LEAK_PATTERNS = [
    "mock_prefix", "mock_scaffold", "user_says", "need_to", "probably", "creator_niche",
    "content_brief", "system_instructions", "internal_reasoning",
    "as_an_ai", "training_data", "prompt_context", "thinking_process",
    "analyze_request", "evaluate_constraint", "issues_header", "improve_header",
    "end_with", "step_header", "key_constraints",
]

_REGEXES = {
    "mock_prefix": re.compile(r"\[(mock|debug|system)[^\]]*\]", re.IGNORECASE),
    "mock_scaffold": re.compile(r"structure: a concrete hook", re.IGNORECASE),
    "user_says": re.compile(r"the user (says|asks|wants|requested)", re.IGNORECASE),
    "need_to": re.compile(r"\bwe need to\b", re.IGNORECASE),
    "probably": re.compile(r"\bprobably (they|you|the user)\b", re.IGNORECASE),
    "creator_niche": re.compile(r"creator niche\s*:", re.IGNORECASE),
    "content_brief": re.compile(r"content brief\s*(\(json\))?\s*:", re.IGNORECASE),
    "system_instructions": re.compile(r"system instructions?", re.IGNORECASE),
    "internal_reasoning": re.compile(r"internal reasoning", re.IGNORECASE),
    "as_an_ai": re.compile(r"as an ai (language )?model", re.IGNORECASE),
    "training_data": re.compile(r"my training (data|cutoff)", re.IGNORECASE),
    "prompt_context": re.compile(r"prompt context\s*:", re.IGNORECASE),
    "thinking_process": re.compile(r"(here'?s a thinking process|thinking process:|thought process:)", re.IGNORECASE),
    "analyze_request": re.compile(r"analyz\w+ the request", re.IGNORECASE),
    "evaluate_constraint": re.compile(r"evaluat\w+ the constraint", re.IGNORECASE),
    "issues_header": re.compile(r"^issues\s*:", re.IGNORECASE | re.MULTILINE),
    "improve_header": re.compile(r"what can improve|recommended changes", re.IGNORECASE),
    "end_with": re.compile(r"\bend with a clear\b", re.IGNORECASE),
    "step_header": re.compile(r"^step \d+\s*[:\-]", re.IGNORECASE | re.MULTILINE),
    "key_constraints": re.compile(r"key constraints?\s*:", re.IGNORECASE),
}


def leak_found(text: str) -> list[str]:
    """Names of leak patterns present in text (empty = clean)."""
    found = []
    for name, rx in _REGEXES.items():
        # mock_prefix is structural scaffolding: only a leak when it survives
        # to user-facing text (scrub removes it first).
        if rx.search(text or ""):
            found.append(name)
    return found


def scrub(text: str) -> str:
    """Remove scaffolding + leaked reasoning lines. Idempotent, never raises."""
    if not text:
        return ""
    out = _REGEXES["mock_prefix"].sub("", text)
    drop = ("mock_scaffold", "user_says", "need_to", "probably", "creator_niche",
            "content_brief", "system_instructions", "internal_reasoning",
            "as_an_ai", "training_data", "prompt_context", "thinking_process",
            "analyze_request", "evaluate_constraint", "issues_header",
            "improve_header", "end_with", "step_header", "key_constraints")
    kept = []
    for line in out.splitlines():
        low = line.strip()
        if not low:
            continue
        if any(_REGEXES[name].search(line) for name in drop):
            continue
        kept.append(line.rstrip())
    return re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()
