"""
SentinelAI — Base Scanner Contract
Abstract base class that all scanners must implement.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseScanner(ABC):
    """
    Abstract base for all vulnerability scanners.

    Each scanner must implement `run(url)` and return a dict
    with a consistent structure:
    {
        "scanner": "<scanner_name>",
        "findings": [ ... ],
        "error": None | "<error message>"
    }
    """

    name: str = "base"

    @abstractmethod
    async def run(self, url: str) -> dict[str, Any]:
        """
        Execute the scan against the given URL.

        Args:
            url: The target URL to scan.

        Returns:
            A dict with keys: scanner, findings, error
        """
        raise NotImplementedError
