"""
Centralized Logging Module for the LUCA 3D Evolution Game.

Junior Dev Note:
----------------
Instead of using `print()` statements scattered across our game code, we use
Python's built-in `logging` module. This allows us to:
1. Record timestamps and severity levels (DEBUG, INFO, WARNING, ERROR).
2. Route logs to both the console and an auditable log file.
3. Easily filter logs during unit testing or Docker container debugging.
"""

import logging
import sys
from typing import List


class MemoryLogHandler(logging.Handler):
    """
    A custom logging handler that stores formatted log entries in memory.

    Junior Dev Note:
    This is super useful for displaying an in-game Developer Audit Console
    and for verifying in unit tests that specific game events were logged!
    """

    def __init__(self, capacity: int = 500) -> None:
        super().__init__()
        self.capacity = capacity
        self.records: List[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Format and store a log record, trimming old records if over capacity."""
        formatted = self.format(record)
        self.records.append(formatted)
        if len(self.records) > self.capacity:
            self.records.pop(0)


# Global in-memory handler instance so tests and UI can inspect recent logs
MEMORY_HANDLER = MemoryLogHandler()


def get_game_logger(name: str = "luca_engine") -> logging.Logger:
    """
    Create or retrieve a configured logger for a specific game module.

    Args:
        name: The module name requesting the logger (e.g., 'luca_engine.cosmos').

    Returns:
        A configured `logging.Logger` instance following PEP8 and audit standards.
    """
    logger = logging.getLogger(name)

    # Only attach handlers once to prevent duplicate log lines
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Standard output stream handler for Docker and CLI visibility
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)

        # Memory buffer handler for regression tests and in-game audit trails
        MEMORY_HANDLER.setLevel(logging.DEBUG)
        MEMORY_HANDLER.setFormatter(formatter)

        logger.addHandler(stream_handler)
        logger.addHandler(MEMORY_HANDLER)
        logger.propagate = False

    return logger
