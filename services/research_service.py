"""Provider-neutral research service for the v0.8 foundation."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Protocol

from core.result import Result


class ResearchSource(Protocol):
    """Minimal source boundary consumed by :class:`ResearchService`."""

    def search(self, query: str, scope: str | None = None) -> Result:
        ...


class ResearchService:
    """Coordinate injected research sources and normalize their evidence."""

    def __init__(self, sources: Iterable[ResearchSource] | None = None) -> None:
        self._invalid_sources = False
        if sources is None:
            self._sources: tuple[ResearchSource, ...] = ()
            return

        try:
            self._sources = tuple(sources)
        except TypeError:
            self._sources = ()
            self._invalid_sources = True

    def research(self, query: str, scope: str | None = None) -> Result:
        if not isinstance(query, str) or not query.strip():
            return Result.fail("Research query is invalid.")

        if scope is not None and (
            not isinstance(scope, str) or not scope.strip()
        ):
            return Result.fail("Research scope is invalid.")

        if self._invalid_sources:
            return Result.fail("Research sources are invalid.")

        if not self._sources:
            return Result.fail("No research source is registered.")

        evidence: list[dict[str, str]] = []

        for index, source in enumerate(self._sources):
            search = getattr(source, "search", None)
            if not callable(search):
                return Result.fail(
                    "Research source is invalid.",
                    metadata={"source_index": index},
                )

            try:
                result = search(query, scope)
            except Exception:
                return Result.fail(
                    "Research source execution failed.",
                    metadata={"source_index": index},
                )

            if not isinstance(result, Result):
                return Result.fail(
                    "Research source returned an invalid Result.",
                    metadata={"source_index": index},
                )

            if not result.success:
                return Result.fail(
                    "Research source failed.",
                    metadata={"source_index": index},
                )

            source_evidence = self._normalize_evidence(result.data)
            if source_evidence is None:
                return Result.fail(
                    "Research source returned malformed evidence.",
                    metadata={"source_index": index},
                )

            evidence.extend(source_evidence)

        return Result.ok(
            data=evidence,
            message="Research completed successfully.",
            metadata={
                "query": query.strip(),
                "scope": scope.strip() if isinstance(scope, str) else None,
                "source_count": len(self._sources),
                "evidence_count": len(evidence),
            },
        )

    @staticmethod
    def _normalize_evidence(data: Any) -> list[dict[str, str]] | None:
        if data is None:
            return []

        if isinstance(data, (str, bytes, Mapping)):
            return None

        try:
            records = list(data)
        except TypeError:
            return None

        normalized: list[dict[str, str]] = []
        for record in records:
            if not isinstance(record, Mapping):
                return None

            values = {
                key: record.get(key)
                for key in ("source", "title", "content", "kind")
            }
            if any(
                not isinstance(value, str) or not value.strip()
                for value in values.values()
            ):
                return None

            if values["kind"].strip().upper() != "FACT":
                return None

            normalized.append(
                {
                    key: values[key].strip()
                    for key in ("source", "title", "content")
                }
                | {"kind": "FACT"}
            )

        return normalized
