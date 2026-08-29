"""Reusable affiliate identity and tracking configuration for v0.8."""

from __future__ import annotations

from typing import Any

from core.result import Result


class AffiliateIdentityService:
    """Store secret-safe affiliate identity records."""

    _SECRET_KEYS = {"secret", "token", "password", "api_key", "apikey", "key"}

    def __init__(self) -> None:
        self._identities: dict[str, dict[str, Any]] = {}
        self._next_id = 1

    def create(
        self,
        network: str,
        account: str,
        campaign: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        if not isinstance(network, str) or not network.strip():
            return Result.fail("Affiliate network is invalid.")
        if not isinstance(account, str) or not account.strip():
            return Result.fail("Affiliate account is invalid.")
        if campaign is not None and (
            not isinstance(campaign, str) or not campaign.strip()
        ):
            return Result.fail("Affiliate campaign is invalid.")
        if parameters is not None and not isinstance(parameters, dict):
            return Result.fail("Affiliate parameters are invalid.")
        if parameters and any(
            any(secret_key in key.lower() for secret_key in self._SECRET_KEYS)
            for key in parameters
            if isinstance(key, str)
        ):
            return Result.fail("Affiliate parameters contain protected data.")

        identity_id = f"affiliate-{self._next_id}"
        self._next_id += 1
        record = {
            "id": identity_id,
            "network": network.strip(),
            "account": account.strip(),
            "campaign": campaign.strip() if isinstance(campaign, str) else None,
            "parameters": dict(parameters or {}),
        }
        self._identities[identity_id] = record
        return Result.ok(
            data=dict(record),
            message="Affiliate identity created successfully.",
            metadata={"identity_id": identity_id},
        )

    def get(self, identity_id: str) -> Result:
        if not isinstance(identity_id, str) or not identity_id.strip():
            return Result.fail("Affiliate identity ID is invalid.")
        record = self._identities.get(identity_id.strip())
        if record is None:
            return Result.fail("Affiliate identity is not registered.")
        return Result.ok(
            data=dict(record),
            message="Affiliate identity retrieved successfully.",
        )
