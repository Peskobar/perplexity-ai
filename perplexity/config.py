"""Runtime configuration shared by sync, async and MCP clients."""

import os
from pathlib import Path

API_BASE_URL = os.environ.get("PERPLEXITY_BASE_URL", "https://www.perplexity.ai").rstrip("/")
API_VERSION = os.environ.get("PERPLEXITY_WEB_API_VERSION", "2.18")
REQUEST_TIMEOUT = float(os.environ.get("PERPLEXITY_REQUEST_TIMEOUT", "60"))

ENDPOINT_AUTH_SESSION = f"{API_BASE_URL}/api/auth/session"
ENDPOINT_AUTH_SIGNIN = f"{API_BASE_URL}/api/auth/signin/email"
ENDPOINT_SSE_ASK = f"{API_BASE_URL}/rest/sse/perplexity_ask"
ENDPOINT_UPLOAD_URL = f"{API_BASE_URL}/rest/uploads/create_upload_url"

SEARCH_MODES = ("auto", "pro", "reasoning", "deep research")
SEARCH_SOURCES = ("web", "scholar", "social")

MODEL_MAPPINGS = {
    "auto": {None: "turbo"},
    "pro": {
        None: "pplx_pro",
        "sonar": "experimental",
        "gpt-5.2": "gpt52",
        "claude-4.5-sonnet": "claude45sonnet",
        "grok-4.1": "grok41nonreasoning",
    },
    "reasoning": {
        None: "pplx_reasoning",
        "gpt-5.2-thinking": "gpt52_thinking",
        "claude-4.5-sonnet-thinking": "claude45sonnetthinking",
        "gemini-3.0-pro": "gemini30pro",
        "kimi-k2-thinking": "kimik2thinking",
        "grok-4.1-reasoning": "grok41reasoning",
    },
    "deep research": {None: "pplx_alpha"},
}

LOG_FORMAT = "% (asctime)s - %(name)s - %(levelname)s - %(message)s".replace("% ", "%")
LOG_LEVEL = os.environ.get("PERPLEXITY_LOG_LEVEL", "INFO").upper()
_STATE_HOME = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
LOG_FILE = os.environ.get(
    "PERPLEXITY_LOG_FILE",
    str(Path(_STATE_HOME) / "perplexity-ai" / "perplexity.log"),
)

DEFAULT_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "dnt": "1",
    "sec-ch-ua": '"Not;A=Brand";v="24", "Chromium";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
}
