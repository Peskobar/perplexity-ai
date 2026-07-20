"""Runtime configuration for the Perplexity client and MCP bridge."""

import os
from pathlib import Path

API_BASE_URL = "https://www.perplexity.ai"
API_VERSION = "2.18"

ENDPOINT_AUTH_SESSION = f"{API_BASE_URL}/api/auth/session"
ENDPOINT_AUTH_SIGNIN = f"{API_BASE_URL}/api/auth/signin/email"
ENDPOINT_SSE_ASK = f"{API_BASE_URL}/rest/sse/perplexity_ask"
ENDPOINT_UPLOAD_URL = f"{API_BASE_URL}/rest/uploads/create_upload_url"

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
