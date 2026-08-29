"""Provider-neutral evidence analysis boundary for v0.8."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from core.result import Result


class AnalysisProvider(Protocol):
    """Optional injected reasoning boundary."""

    def analyze(
        self,
        evidence: list[dict[str, Any]],
        question: str | None = None,
    ) -> Result:
        ...


class AnalysisService:
    """Validate and normalize classified evidence without inventing facts."""

    _KINDS = {
        "FACT",
        "HYPOTHESIS",
        "RECOMMENDATION",
        "ACTION",
        "RESULT",
    }

    def __init__(self, analyzer: AnalysisProvider | None = None) -> None:
        self._analyzer = analyzer

    def analyze(
        self,
        evidence: Sequence[Mapping[str, Any]],
        question: str | None = None,
    ) -> Result:
        if isinstance(evidence, (str, bytes)) or not isinstance(
            evidence, Sequence
        ):
            return Result.fail("Analysis evidence is invalid.")

        if question is not None and (
            not isinstance(question, str) or not question.strip()
        ):
            return Result.fail("Analysis question is invalid.")

        normalized = self._normalize_records(evidence)
        if normalized is None:
            return Result.fail("Analysis evidence is malformed.")

        if self._analyzer is None:
            return self._success(normalized, question)

        analyze = getattr(self._analyzer, "analyze", None)
        if not callable(analyze):
            return Result.fail("Analysis provider is invalid.")

        try:
            result = analyze(
                normalized,
                question.strip() if isinstance(question, str) else None,
            )
        except Exception:
            return Result.fail("Analysis provider execution failed.")

        if not isinstance(result, Result) or not result.success:
            return Result.fail("Analysis provider failed.")

        analyzed = self._normalize_records(result.data)
        if analyzed is None:
            return Result.fail("Analysis provider returned malformed data.")

        return self._success(analyzed, question)

    @classmethod
    def _normalize_records(
        cls,
        records: Any,
    ) -> list[dict[str, Any]] | None:
        if isinstance(records, (str, bytes, Mapping)) or not isinstance(
            records, Sequence
        ):
            return None

        normalized: list[dict[str, Any]] = []
        for record in records:
            if not isinstance(record, Mapping):
                return None

            kind = record.get("kind")
            content = record.get("content")
            if not isinstance(kind, str) or kind.strip().upper() not in cls._KINDS:
                return None
            if not isinstance(content, str) or not content.strip():
                return None

            item = dict(record)
            item["kind"] = kind.strip().upper()
            item["content"] = content.strip()
            normalized.append(item)

        return normalized

    @classmethod
    def _success(
        cls,
        records: list[dict[str, Any]],
        question: str | None,
    ) -> Result:
        counts = {kind: 0 for kind in sorted(cls._KINDS)}
        for record in records:
            counts[record["kind"]] += 1

        return Result.ok(
            data=records,
            message="Analysis completed successfully.",
            metadata={
                "question": question.strip() if isinstance(question, str) else None,
                "count": len(records),
                "counts": counts,
            },
        )
