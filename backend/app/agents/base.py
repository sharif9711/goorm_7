from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    name: str = "base_agent"

    @abstractmethod
    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute agent logic and return results to merge into context."""

    def log(self, message: str) -> None:
        print(f"[{self.name}] {message}")
