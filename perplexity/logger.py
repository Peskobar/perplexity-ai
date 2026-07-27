"""Central logging helpers.

MCP stdio reserves stdout for JSON-RPC, so console logs always go to stderr.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .config import LOG_FILE, LOG_FORMAT, LOG_LEVEL


def setup_logger(
    name: str = "perplexity",
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    console: bool = True,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, (level or LOG_LEVEL).upper(), logging.INFO))
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT)

    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    selected_log_file = log_file or LOG_FILE
    if selected_log_file:
        file_path = Path(selected_log_file).expanduser()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"perplexity.{name}")
