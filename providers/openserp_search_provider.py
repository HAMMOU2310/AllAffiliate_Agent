"""OpenSERP OSS HTTP adapter implementing the ResearchSource protocol."""

from __future__ import annotations

import os
from typing import Any

import requests as _requests
from requests.exceptions import ConnectionError as _ConnectionError
from requests.exceptions import Timeout as _Timeout

from core.result import Result

_SCOPE_ENGINE_MAP: dict[str, str] = {
    "general": "google,bing",
    "news": "bing,google",
    "finance": "google,bing",
}


class OpenSERPSearchProvider:
    """Provider-owned OpenSERP OSS search adapter."""

    def __init__(
        self,
        base_url: str | None = None,
        engines: str | None = None,
        mode: str | None = None,
        limit: int | None = None,
        extract: int | None = None,
        timeout: int | None = None,
    ) -> None:
        self._base_url = (
            base_url
            or os.getenv("OPENSERP_BASE_URL", "http://127.0.0.1:7000")
        ).rstrip("/")
        self._engines = engines or os.getenv("OPENSERP_ENGINES", "google,bing")
        self._mode = mode or os.getenv("OPENSERP_MODE", "balanced")
        self._limit = max(1, min(limit or int(os.getenv("OPENSERP_LIMIT", "5")), 100))
        self._extract = max(0, min(extract if extract is not None else int(os.getenv("OPENSERP_EXTRACT", "0")), 5))
        self._timeout = timeout or int(os.getenv("OPENSERP_TIMEOUT_SECONDS", "30"))

    def search(self, query: str, scope: str | None = None) -> Result:
        if not isinstance(query, str) or not query.strip():
            return Result.fail("Web search query is invalid.")

        if scope is not None and (not isinstance(scope, str) or not scope.strip()):
            return Result.fail("Web search scope is invalid.")

        engines = _SCOPE_ENGINE_MAP.get(
            scope.strip().lower() if isinstance(scope, str) else "",
            self._engines,
        )

        params: dict[str, Any] = {
            "text": query.strip(),
            "engines": engines,
            "mode": self._mode,
            "limit": self._limit,
            "dedupe": "true",
            "merge": "true",
            "format": "json",
        }

        if self._extract > 0:
            params["extract"] = self._extract

        try:
            response = _requests.get(
                f"{self._base_url}/mega/search",
                params=params,
                timeout=self._timeout,
            )
        except _Timeout:
            return Result.fail("Search request timed out.")
        except _ConnectionError:
            return Result.fail("Search service is not available.")
        except Exception:
            return Result.fail("Search execution failed.")

        return self._handle_response(response)

    def _handle_response(self, response: Any) -> Result:
        status = response.status_code

        if status == 400:
            return Result.fail("Search request is invalid.")
        if status == 403:
            return Result.fail("Search access is forbidden.")
        if status == 429:
            return Result.fail("Search rate limit exceeded.")
        if status >= 500:
            return Result.fail("Search service error.")
        if status >= 400:
            return Result.fail("Search request failed.")

        try:
            data = response.json()
        except (ValueError, TypeError):
            return Result.fail("Search returned an invalid response.")

        if not isinstance(data, dict):
            return Result.fail("Search returned an invalid response.")

        raw_results = data.get("results")
        if not isinstance(raw_results, list):
            return Result.fail("Search returned an invalid response.")

        meta = data.get("meta")
        if isinstance(meta, dict):
            engines_failed = meta.get("engines_failed")
            engines_responded = meta.get("engines_responded")
            if (
                isinstance(engines_failed, list)
                and len(engines_failed) > 0
                and isinstance(engines_responded, list)
                and len(engines_responded) == 0
            ):
                return Result.fail("Search engines failed.")

        evidence = self._normalize_results(raw_results)
        if not evidence:
            return Result.ok(data=[], message="No results found.")

        return Result.ok(
            data=evidence,
            message="Web search completed successfully.",
        )

    @staticmethod
    def _normalize_results(raw_results: list[dict[str, Any]]) -> list[dict[str, str]]:
        evidence: list[dict[str, str]] = []
        for item in raw_results:
            if not isinstance(item, dict):
                continue

            source = str(item.get("url", "")).strip()
            title = str(item.get("title", "")).strip()

            extracted = item.get("extracted")
            if isinstance(extracted, dict):
                content = str(extracted.get("content", "")).strip()
            else:
                content = str(item.get("snippet", "")).strip()

            if source and title and content:
                evidence.append(
                    {"source": source, "title": title, "content": content, "kind": "FACT"}
                )
        return evidence
