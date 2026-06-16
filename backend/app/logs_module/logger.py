"""
Module 4 – Logging
Structured JSON logging with daily rotation.
Logs are written to /logs/app.log (mounted volume in Docker).
"""

import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import json
from datetime import datetime
from typing import Any, Dict


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"


class JSONFormatter(logging.Formatter):
    """Format log records as JSON lines for easy parsing (e.g. by Logstash/Grafana Loki)."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
        return json.dumps(log_entry)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure root logger with:
    - Console handler (plain text)
    - File handler (JSON, daily rotation, 30 days retention)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )

    # File (JSON)
    file_handler = TimedRotatingFileHandler(
        filename=str(LOG_FILE),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setFormatter(JSONFormatter())

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Silence noisy third-party loggers
    for noisy in ("uvicorn.access", "httpx", "multipart"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return root_logger


# Module-level convenience getter
def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
