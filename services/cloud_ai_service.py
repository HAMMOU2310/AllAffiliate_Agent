"""
services/cloud_ai_service.py

Provider-neutral Cloud AI service boundary for v0.7.
"""

from __future__ import annotations

from typing import Protocol

from core.result import Result


class CloudAIProvider(Protocol):
    """Public provider boundary for cloud AI implementations."""

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        parameters: dict | None = None,
    ) -> Result:
        ...


class CloudAIService:
    """
    Unified service for registering and invoking Cloud AI providers.

    The first successfully registered provider becomes the default provider.
    """

    def __init__(self):
        self._providers: dict[str, CloudAIProvider] = {}
        self._default_provider: str | None = None

    def register_provider(
        self,
        name: str,
        provider: CloudAIProvider,
    ) -> Result:
        if not isinstance(name, str) or not name.strip():
            return Result.fail("Provider name is invalid.")

        if provider is None or not callable(getattr(provider, "generate", None)):
            return Result.fail("Provider is invalid.")

        if name in self._providers:
            return Result.fail(f"Provider already registered: {name}")

        self._providers[name] = provider

        if self._default_provider is None:
            self._default_provider = name

        return Result.ok(
            data=provider,
            message=f"Provider registered successfully: {name}",
            metadata={
                "provider": name,
                "default": self._default_provider == name,
                "count": len(self._providers),
            },
        )

    def remove_provider(self, name: str) -> Result:
        if not isinstance(name, str) or not name.strip():
            return Result.fail("Provider name is invalid.")

        if name not in self._providers:
            return Result.fail(f"Provider not registered: {name}")

        provider = self._providers.pop(name)

        if self._default_provider == name:
            self._default_provider = (
                next(iter(self._providers))
                if self._providers
                else None
            )

        return Result.ok(
            data=provider,
            message=f"Provider removed successfully: {name}",
            metadata={
                "provider": name,
                "default": self._default_provider,
                "count": len(self._providers),
            },
        )

    def get_provider(self, name: str) -> Result:
        if not isinstance(name, str) or not name.strip():
            return Result.fail("Provider name is invalid.")

        provider = self._providers.get(name)

        if provider is None:
            return Result.fail(f"Provider not registered: {name}")

        return Result.ok(
            data=provider,
            message=f"Provider retrieved successfully: {name}",
            metadata={
                "provider": name,
                "default": self._default_provider == name,
            },
        )

    def list_providers(self) -> Result:
        return Result.ok(
            data=sorted(self._providers),
            message="Cloud AI providers listed successfully.",
            metadata={
                "count": len(self._providers),
                "default": self._default_provider,
            },
        )

    def generate(
        self,
        prompt: str,
        provider: str | None = None,
        model: str | None = None,
        parameters: dict | None = None,
    ) -> Result:
        if not isinstance(prompt, str) or not prompt.strip():
            return Result.fail("Prompt is invalid.")

        provider_name = provider or self._default_provider

        if not provider_name:
            return Result.fail("No Cloud AI provider is registered.")

        selected = self._providers.get(provider_name)

        if selected is None:
            return Result.fail(f"Provider not registered: {provider_name}")

        try:
            result = selected.generate(
                prompt=prompt,
                model=model,
                parameters=parameters,
            )
        except Exception as exc:
            return Result.fail(
                "Cloud AI provider execution failed.",
                errors=[str(exc)],
                metadata={"provider": provider_name},
            )

        if not isinstance(result, Result):
            return Result.fail(
                "Cloud AI provider returned an invalid Result.",
                metadata={"provider": provider_name},
            )

        if not result.success:
            return Result.fail(
                result.message or "Cloud AI provider execution failed.",
                errors=result.errors,
                metadata={
                    **result.metadata,
                    "provider": provider_name,
                },
            )

        return Result.ok(
            data=result.data,
            message=result.message,
            metadata={
                **result.metadata,
                "provider": provider_name,
            },
        )
