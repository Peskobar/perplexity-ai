import json

import pytest

from perplexity.protocol import (
    ProtocolError,
    build_search_payload,
    file_size,
    parse_sse_event,
    validate_search,
)


def test_parse_nested_final_answer():
    nested_answer = json.dumps({"answer": "Gotowa odpowiedź", "chunks": ["a", "b"]})
    nested_text = json.dumps(
        [
            {"step_type": "SEARCH", "content": {}},
            {"step_type": "FINAL", "content": {"answer": nested_answer}},
        ]
    )
    raw = (
        "event: message\r\n"
        f"data: {json.dumps({'text': nested_text, 'backend_uuid': 'thread-1'})}\r\n\r\n"
    )

    event_name, payload = parse_sse_event(raw)

    assert event_name == "message"
    assert payload["answer"] == "Gotowa odpowiedź"
    assert payload["chunks"] == ["a", "b"]
    assert isinstance(payload["text"], list)


def test_parse_blocks_payload_without_destroying_structure():
    original = {
        "blocks": [
            {
                "intended_usage": "ask_text",
                "markdown_block": {"answer": "Odpowiedź blokowa"},
            }
        ]
    }
    event_name, payload = parse_sse_event(
        f"event: message\ndata: {json.dumps(original)}\n\n"
    )

    assert event_name == "message"
    assert payload == original


def test_end_of_stream_event():
    assert parse_sse_event("event: end_of_stream\ndata: {}") == (
        "end_of_stream",
        None,
    )


def test_invalid_json_is_ignored():
    assert parse_sse_event("event: message\ndata: {broken") == ("invalid", None)


def test_current_reasoning_model_mapping_and_follow_up():
    payload = build_search_payload(
        "Kontynuuj analizę",
        mode="reasoning",
        model="gemini-3.0-pro",
        sources=["web", "scholar"],
        uploaded_files=["https://files.example/a.pdf"],
        follow_up={"backend_uuid": "thread-42", "attachments": ["old.pdf"]},
        language="pl-PL",
        incognito=True,
    )

    params = payload["params"]
    assert params["model_preference"] == "gemini30pro"
    assert params["last_backend_uuid"] == "thread-42"
    assert params["attachments"] == ["https://files.example/a.pdf", "old.pdf"]
    assert params["sources"] == ["web", "scholar"]
    assert params["language"] == "pl-PL"
    assert params["is_incognito"] is True


def test_rejects_stale_or_unknown_model():
    with pytest.raises(ProtocolError):
        validate_search("pro", "gpt-4o", ["web"])


def test_rejects_unknown_source():
    with pytest.raises(ProtocolError):
        validate_search("auto", None, ["private-index"])


def test_file_size_counts_transmitted_bytes():
    assert file_size(b"1234") == 4
    assert file_size("ą") == 2
