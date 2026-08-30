import logging
import sys
import time
from typing import Dict, Any


class VeritasFormatter(logging.Formatter):
    """Clean structured log formatter."""
    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, self.datefmt)
        level = record.levelname
        msg = record.getMessage()
        return f"[{timestamp}] [{level:7s}] [{record.name}] {msg}"


def setup_logger(name: str = "veritas_ai") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        # On Windows, wrap stdout safely
        stream = sys.stdout
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
        handler = logging.StreamHandler(stream)
        handler.setFormatter(VeritasFormatter(datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = setup_logger()
