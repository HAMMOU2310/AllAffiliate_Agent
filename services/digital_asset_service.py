"""Isolated digital asset registry for v0.8."""

from __future__ import annotations

from typing import Any

from core.result import Result


class DigitalAssetService:
    """Store reusable digital asset records without external side effects."""

    _ASSET_TYPES = {
        "website",
        "landing_page",
        "product",
        "affiliate_link",
        "video",
        "channel",
        "campaign",
        "social_account",
        "content_asset",
        "image",
    }
    _SECRET_KEYS = {"secret", "token", "password", "api_key", "apikey"}

    def __init__(self) -> None:
        self._assets: dict[str, dict[str, Any]] = {}
        self._next_id = 1

    def register(
        self,
        asset_type: str,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> Result:
        if not isinstance(asset_type, str) or asset_type.strip().lower() not in self._ASSET_TYPES:
            return Result.fail("Digital asset type is invalid.")
        if not isinstance(name, str) or not name.strip():
            return Result.fail("Digital asset name is invalid.")
        if metadata is not None and not isinstance(metadata, dict):
            return Result.fail("Digital asset metadata is invalid.")
        if metadata and any(
            any(secret_key in key.lower() for secret_key in self._SECRET_KEYS)
            for key in metadata
            if isinstance(key, str)
        ):
            return Result.fail("Digital asset metadata contains protected data.")

        asset_id = f"asset-{self._next_id}"
        self._next_id += 1
        record = {
            "id": asset_id,
            "type": asset_type.strip().lower(),
            "name": name.strip(),
            "metadata": dict(metadata or {}),
        }
        self._assets[asset_id] = record
        return Result.ok(
            data=dict(record),
            message="Digital asset registered successfully.",
            metadata={"asset_id": asset_id, "count": len(self._assets)},
        )

    def get(self, asset_id: str) -> Result:
        if not isinstance(asset_id, str) or not asset_id.strip():
            return Result.fail("Digital asset ID is invalid.")
        record = self._assets.get(asset_id.strip())
        if record is None:
            return Result.fail("Digital asset is not registered.")
        return Result.ok(data=dict(record), message="Digital asset retrieved successfully.")

    def list_assets(self, asset_type: str | None = None) -> Result:
        normalized_type = None
        if asset_type is not None:
            if not isinstance(asset_type, str) or not asset_type.strip().lower() in self._ASSET_TYPES:
                return Result.fail("Digital asset type is invalid.")
            normalized_type = asset_type.strip().lower()

        records = [
            dict(record)
            for record in self._assets.values()
            if normalized_type is None or record["type"] == normalized_type
        ]
        return Result.ok(
            data=records,
            message="Digital assets listed successfully.",
            metadata={"count": len(records), "type": normalized_type},
        )
