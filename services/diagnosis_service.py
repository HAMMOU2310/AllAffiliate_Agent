"""Evidence-preserving diagnosis boundary for v0.9."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from core.result import Result


class DiagnosisAnalyzer(Protocol):
    def analyze(self, asset_id: str, observations: list[dict[str, Any]]) -> Result:
        ...


class DiagnosisService:
    _KINDS = {"FACT", "HYPOTHESIS", "RECOMMENDATION"}

    def __init__(self, analyzer: DiagnosisAnalyzer | None = None) -> None:
        self._analyzer = analyzer

    def diagnose(self, asset_id: str, observations: Sequence[Mapping[str, Any]]) -> Result:
        if not isinstance(asset_id, str) or not asset_id.strip():
            return Result.fail("Diagnosis asset ID is invalid.")
        records = self._normalize(observations, default_fact=True)
        if records is None:
            return Result.fail("Diagnosis observations are malformed.")
        if self._analyzer is not None:
            analyze = getattr(self._analyzer, "analyze", None)
            if not callable(analyze):
                return Result.fail("Diagnosis analyzer is invalid.")
            try:
                result = analyze(asset_id.strip(), records)
            except Exception:
                return Result.fail("Diagnosis analyzer execution failed.")
            if not isinstance(result, Result) or not result.success:
                return Result.fail("Diagnosis analyzer failed.")
            records = self._normalize(result.data, default_fact=False)
            if records is None:
                return Result.fail("Diagnosis analyzer returned malformed data.")
        return Result.ok(
            data=records,
            message="Diagnosis completed successfully.",
            metadata={"asset_id": asset_id.strip(), "count": len(records)},
        )

    @classmethod
    def _normalize(cls, records: Any, default_fact: bool) -> list[dict[str, Any]] | None:
        if isinstance(records, (str, bytes, Mapping)) or not isinstance(records, Sequence):
            return None
        normalized = []
        for record in records:
            if not isinstance(record, Mapping) or not isinstance(record.get("content"), str):
                return None
            item = dict(record)
            kind = item.get("kind", "FACT" if default_fact else None)
            if not isinstance(kind, str) or kind.upper() not in cls._KINDS:
                return None
            item["kind"] = kind.upper()
            item["content"] = item["content"].strip()
            if not item["content"]:
                return None
            normalized.append(item)
        return normalized
