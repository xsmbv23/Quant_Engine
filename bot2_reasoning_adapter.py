"""Provider-neutral reasoning boundary for BOT2.

This module deliberately does not assume a specific model vendor. The worker can
use any OpenAI-compatible chat-completions endpoint configured by environment.
No credentials are stored in source or deliberation records.
"""
from __future__ import annotations

import json
import os
import urllib.request


class ReasoningNotConfigured(RuntimeError):
    pass


BASE_URL = os.environ.get("LLM_BASE_URL", "").rstrip("/")
API_KEY = os.environ.get("LLM_API_KEY", "")
MODEL = os.environ.get("LLM_MODEL", "")
TIMEOUT = int(os.environ.get("LLM_TIMEOUT_SECONDS", "90"))


def configured() -> bool:
    return bool(BASE_URL and API_KEY and MODEL)


def reason(system_prompt: str, user_prompt: str) -> dict:
    if not configured():
        raise ReasoningNotConfigured(
            "BOT2_LLM_REASONING_NOT_CONFIGURED: set LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL"
        )

    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
    }).encode("utf-8")

    request = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "bot2-quant-worker",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        result = json.loads(response.read().decode("utf-8"))

    choices = result.get("choices") or []
    if not choices:
        raise RuntimeError("LLM_EMPTY_RESPONSE")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if not content:
        raise RuntimeError("LLM_EMPTY_CONTENT")
    return {
        "model": MODEL,
        "content": content,
    }
