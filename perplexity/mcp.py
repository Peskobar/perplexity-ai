"""MCP bridge for the existing Perplexity client.

The bridge preserves the account/session modules already present in this fork.
It never exposes raw cookies to MCP clients and supports both current block-based
responses and the older nested ``text`` response format used by this repository.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

from perplexity import Client
from perplexity.logger import setup_logger

logger = setup_logger("perplexity.mcp")
client: Client

mcp = FastMCP(
    "perplexity",
    host=os.environ.get("MCP_HOST", "127.0.0.1"),
    port=int(os.environ.get("MCP_PORT", "8000")),
)


def _decode_json_maybe(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def _extract_answer(response: Any) -> str:
    """Extract text from old and new Perplexity web response formats."""
    if response is None:
        return ""
    if isinstance(response, str):
        return response
    if isinstance(response, list):
        for item in reversed(response):
            answer = _extract_answer(item)
            if answer:
                return answer
        return ""
    if not isinstance(response, dict):
        return str(response)

    direct = response.get("answer")
    if isinstance(direct, str) and direct:
        return direct

    for block in response.get("blocks", []) or []:
        if not isinstance(block, dict):
            continue
        markdown = block.get("markdown_block") or {}
        if isinstance(markdown, dict):
            answer = markdown.get("answer")
            if isinstance(answer, str) and answer:
                return answer
            chunks = markdown.get("chunks")
            if isinstance(chunks, list) and chunks:
                return "".join(str(chunk) for chunk in chunks)

    text = _decode_json_maybe(response.get("text"))
    if isinstance(text, dict):
        answer = text.get("answer")
        if isinstance(answer, str) and answer:
            return answer
        chunks = text.get("chunks")
        if isinstance(chunks, list) and chunks:
            return "".join(str(chunk) for chunk in chunks)

    if isinstance(text, list):
        for step in reversed(text):
            if not isinstance(step, dict):
                continue
            content = step.get("content") or {}
            if isinstance(content, str):
                content = _decode_json_maybe(content)
            if not isinstance(content, dict):
                continue
            answer_data = _decode_json_maybe(content.get("answer"))
            if isinstance(answer_data, dict):
                answer = answer_data.get("answer")
                if isinstance(answer, str) and answer:
                    return answer
                chunks = answer_data.get("chunks")
                if isinstance(chunks, list) and chunks:
                    return "".join(str(chunk) for chunk in chunks)
            elif isinstance(answer_data, str) and answer_data:
                return answer_data

    return ""


def _normalize_cookies(raw: Any) -> Dict[str, str]:
    if isinstance(raw, dict):
        return {str(key): str(value) for key, value in raw.items()}
    if isinstance(raw, list):
        normalized: Dict[str, str] = {}
        for cookie in raw:
            if isinstance(cookie, dict) and cookie.get("name") is not None:
                normalized[str(cookie["name"])] = str(cookie.get("value", ""))
        return normalized
    raise ValueError("Cookies must be a JSON object or a browser-exported JSON list.")


def _load_cookies() -> Dict[str, str]:
    inline = os.environ.get("PERPLEXITY_COOKIES", "").strip()
    cookie_file = os.environ.get("PERPLEXITY_COOKIES_FILE", "").strip()

    if inline:
        try:
            return _normalize_cookies(json.loads(inline))
        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError(f"Invalid PERPLEXITY_COOKIES: {exc}") from exc

    if cookie_file:
        path = Path(cookie_file).expanduser()
        try:
            return _normalize_cookies(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError(f"Cannot load PERPLEXITY_COOKIES_FILE: {exc}") from exc

    return {}


def _run_query(query: str, *, mode: str, sources=None) -> str:
    response = client.search(query, mode=mode, sources=sources or ["web"])
    answer = _extract_answer(response)
    if not answer:
        raise RuntimeError("Perplexity returned a response, but no answer text could be extracted.")
    return answer


def perplexity_ask(query: str) -> str:
    """Ask a general question using Perplexity auto mode."""
    return _run_query(query, mode="auto")


def perplexity_search(query: str) -> str:
    """Search the current web using authenticated Perplexity Pro mode."""
    return _run_query(query, mode="pro", sources=["web"])


def perplexity_reason(query: str) -> str:
    """Use Perplexity reasoning mode for a multi-step problem."""
    return _run_query(query, mode="reasoning")


def perplexity_research(query: str) -> str:
    """Run Perplexity deep-research mode for a comprehensive report."""
    return _run_query(query, mode="deep research")


def perplexity_account_status() -> str:
    """Return non-secret information about the active local session."""
    copilot = getattr(client, "copilot", 0)
    uploads = getattr(client, "file_upload", 0)
    status = {
        "authenticated": bool(getattr(client, "own", False)),
        "pro_queries": "unlimited" if copilot == float("inf") else copilot,
        "file_uploads": "unlimited" if uploads == float("inf") else uploads,
        "cookies_exposed": False,
    }
    return json.dumps(status, ensure_ascii=False)


def main() -> None:
    global client

    try:
        cookies = _load_cookies()
    except RuntimeError as exc:
        sys.exit(f"ERROR: {exc}")

    client = Client(cookies)

    mcp.tool()(perplexity_ask)
    mcp.tool()(perplexity_account_status)

    if client.own:
        mcp.tool()(perplexity_search)
        mcp.tool()(perplexity_reason)
        mcp.tool()(perplexity_research)
        logger.info("Authenticated session loaded; all MCP tools enabled.")
    else:
        logger.warning(
            "No session cookies loaded; anonymous mode exposes only "
            "perplexity_ask and perplexity_account_status."
        )

    transport = os.environ.get("MCP_TRANSPORT", "stdio").strip().lower()
    if transport == "stdio":
        mcp.run()
    elif transport in {"http", "streamable-http"}:
        mcp.run(transport="streamable-http")
    else:
        sys.exit("ERROR: MCP_TRANSPORT must be 'stdio' or 'http'.")


if __name__ == "__main__":
    main()
