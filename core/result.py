"""
core/result.py

Unified Result object used across the entire project.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Result:
    """
    Represents the outcome of any operation inside the project.

    This is the unified contract between Agents, Services and Tools.
    """

    success: bool
    message: str = ""

    data: Any = None

    errors: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    timestamp: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def ok(
        cls,
        data: Any = None,
        message: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> "Result":
        return cls(
            success=True,
            message=message,
            data=data,
            metadata=metadata or {},
        )

    @classmethod
    def fail(
        cls,
        message: str,
        errors: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "Result":
        return cls(
            success=False,
            message=message,
            errors=errors or [],
            metadata=metadata or {},
        )

    @property
    def failed(self) -> bool:
        return not self.success

    def __bool__(self) -> bool:
        return self.success

    def __repr__(self) -> str:
        return (
            f"Result(success={self.success}, "
            f"message={self.message!r})"
        )