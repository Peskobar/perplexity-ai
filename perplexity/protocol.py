"""Helpers for building Perplexity web payloads and parsing SSE events."""

import json
from typing import Any, Iterable, Optional, Tuple
from uuid import uuid4

from .config import API_VERSION, MODEL_MAPPINGS, SEARCH_MODES, SEARCH_SOURCES


class ProtocolError(ValueError):
    """Raised when a local request does not match the supported web protocol."""


def validate_search(mode: str, model: Optional[str], sources: Iterable[str]) -> None:
    if mode not in SEARCH_MODES:
        raise ProtocolError(f"Unsupported search mode: {mode}")
    if model not in MODEL_MAPPINGS[mode]:
        allowed = [name for name in MODEL_MAPPINGS[mode] if name is not None]
        raise ProtocolError(f"Unsupported model for {mode}: {model}. Allowed: {allowed}")

    invalid_sources = [source for source in sources if source not in SEARCH_SOURCES]
    if invalid_sources:
        raise ProtocolError(f"Unsupported sources: {invalid_sources}")


def build_search_payload(
    query: str,
    *,
    mode: str,
    model: Optional[str],
    sources: Iterable[str],
    uploaded_files: Optional[Iterable[str]] = None,
    follow_up: Optional[dict] = None,
    language: str = "en-US",
    incognito: bool = False,
) -> dict:
    sources = list(sources)
    validate_search(mode, model, sources)
    uploaded_files = list(uploaded_files or [])
    follow_up = follow_up or {}
    previous_attachments = list(follow_up.get("attachments") or [])

    return {
        "query_str": query,
        "params": {
            "attachments": uploaded_files + previous_attachments,
            "frontend_context_uuid": str(uuid4()),
            "frontend_uuid": str(uuid4()),
            "is_incognito": incognito,
            "language": language,
            "last_backend_uuid": follow_up.get("backend_uuid"),
            "mode": "concise" if mode == "auto" else "copilot",
            "model_preference": MODEL_MAPPINGS[mode][model],
            "source": "default",
            "sources": sources,
            "version": API_VERSION,
        },
    }


def parse_sse_event(raw_event: Any) -> Tuple[str, Optional[dict]]:
    """Return ``(event_name, payload)`` for one complete SSE event block."""

    if isinstance(raw_event, bytes):
        text = raw_event.decode("utf-8", errors="replace")
    else:
        text = str(raw_event)

    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        return "empty", None

    event_name = "message"
    data_lines = []
    for line in normalized.split("\n"):
        if line.startswith("event:"):
            event_name = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            data_lines.append(line.split(":", 1)[1].lstrip())

    if event_name == "end_of_stream":
        return event_name, None
    if not data_lines:
        return event_name, None

    try:
        payload = json.loads("\n".join(data_lines))
    except json.JSONDecodeError:
        return "invalid", None

    if not isinstance(payload, dict):
        return event_name, {"value": payload}

    nested_text = payload.get("text")
    if isinstance(nested_text, str) and nested_text:
        try:
            nested_text = json.loads(nested_text)
            payload["text"] = nested_text
        except json.JSONDecodeError:
            pass

    if isinstance(nested_text, list):
        for step in nested_text:
            if not isinstance(step, dict) or step.get("step_type") != "FINAL":
                continue
            content = step.get("content") or {}
            answer = content.get("answer")
            if isinstance(answer, str):
                try:
                    answer = json.loads(answer)
                except json.JSONDecodeError:
                    answer = {"answer": answer}
            if isinstance(answer, dict):
                payload.setdefault("answer", answer.get("answer", ""))
                payload.setdefault("chunks", answer.get("chunks", []))
            break

    return event_name, payload


def file_size(file_data: Any) -> int:
    """Return the transmitted byte size instead of Python object overhead."""

    if isinstance(file_data, str):
        return len(file_data.encode("utf-8"))
    if isinstance(file_data, (bytes, bytearray, memoryview)):
        return len(file_data)
    try:
        return len(file_data)
    except TypeError as exc:
        raise ProtocolError("File data must provide a byte length") from exc
