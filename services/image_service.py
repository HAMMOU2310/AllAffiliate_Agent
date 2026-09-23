"""Provider-neutral image service boundary for v0.6."""

from __future__ import annotations

from typing import Any, Protocol

from core.result import Result


class ImageGenerator(Protocol):
    """Provider boundary for AI image generation."""

    def generate(
        self,
        prompt: str,
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        ...


class ImageProcessor(Protocol):
    """Provider boundary for local image processing."""

    def process(
        self,
        source: str,
        operation: str,
        params: dict[str, Any] | None = None,
    ) -> Result:
        ...


class ImageService:
    """Service boundary for image operations."""

    _OPERATIONS = frozenset({
        "generate",
        "resize",
        "crop",
        "thumbnail",
        "convert",
        "validate",
        "metadata",
    })

    def __init__(
        self,
        generator: ImageGenerator | None = None,
        processor: ImageProcessor | None = None,
    ) -> None:
        self._generator = generator
        self._processor = processor

    def execute(self, command: str) -> Result:
        """Main entry point for image commands."""
        if not isinstance(command, str) or not command.strip():
            return Result.fail("Image command is invalid.")

        body = command.strip()
        parts = body.split(maxsplit=1)
        operation = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        if operation not in self._OPERATIONS:
            return Result.fail(
                f"Unsupported image operation: {operation}. "
                f"Supported: {', '.join(sorted(self._OPERATIONS))}"
            )

        if operation == "generate":
            return self.generate(args)

        return self._process_operation(operation, args)

    def generate(
        self,
        prompt: str,
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        if not isinstance(prompt, str) or not prompt.strip():
            return Result.fail("Image prompt is invalid.")

        if self._generator is None:
            return Result.fail("No image generation provider is registered.")

        generate_fn = getattr(self._generator, "generate", None)
        if not callable(generate_fn):
            return Result.fail("Image generation provider is invalid.")

        try:
            result = generate_fn(prompt.strip(), parameters)
        except Exception:
            return Result.fail("Image generation provider execution failed.")

        if not isinstance(result, Result):
            return Result.fail(
                "Image generation provider returned an invalid Result."
            )

        return result

    def _process_operation(self, operation: str, args: str) -> Result:
        if self._processor is None:
            return Result.fail("No image processing provider is registered.")

        process_fn = getattr(self._processor, "process", None)
        if not callable(process_fn):
            return Result.fail("Image processing provider is invalid.")

        if not args or not args.strip():
            return Result.fail(f"Image {operation} requires input.")

        params = self._parse_process_args(operation, args.strip())

        try:
            result = process_fn(
                params.pop("source", ""),
                operation,
                params or None,
            )
        except Exception:
            return Result.fail(
                f"Image {operation} provider execution failed."
            )

        if not isinstance(result, Result):
            return Result.fail(
                f"Image {operation} provider returned an invalid Result."
            )

        return result

    @staticmethod
    def _parse_process_args(operation: str, args: str) -> dict[str, Any]:
        parts = args.split()
        params: dict[str, Any] = {}

        if not parts:
            return params

        params["source"] = parts[0]

        if operation == "resize" and len(parts) >= 3:
            try:
                params["width"] = int(parts[1])
                params["height"] = int(parts[2])
            except ValueError:
                pass

        elif operation == "crop" and len(parts) >= 5:
            try:
                params["x"] = int(parts[1])
                params["y"] = int(parts[2])
                params["width"] = int(parts[3])
                params["height"] = int(parts[4])
            except ValueError:
                pass

        elif operation == "thumbnail" and len(parts) >= 2:
            try:
                params["size"] = int(parts[1])
            except ValueError:
                pass

        elif operation == "convert" and len(parts) >= 2:
            params["format"] = parts[1]

        return params
