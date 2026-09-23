"""Google Gemini implementation of the ImageGenerator Protocol."""

from __future__ import annotations

import os
import tempfile
from typing import Any

from core.result import Result

_DEFAULT_MODEL = "imagen-3.0-generate-002"

_MIME_TO_FORMAT = {
    "image/png": "PNG",
    "image/jpeg": "JPEG",
    "image/webp": "WEBP",
}


def _create_gemini_client(api_key: str) -> Any:
    """Create the Google GenAI client without exposing provider credentials."""
    try:
        from google import genai
    except Exception as exc:
        raise RuntimeError("Google GenAI SDK is unavailable.") from exc

    try:
        return genai.Client(api_key=api_key)
    except Exception as exc:
        raise RuntimeError("Gemini client configuration is invalid.") from exc


class GeminiImageProvider:
    """Provider-owned Google Gemini image generation adapter."""

    def __init__(self, output_dir: str | None = None) -> None:
        self._client: Any | None = None
        self._output_dir = output_dir

    def generate(
        self,
        prompt: str,
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        if not isinstance(prompt, str) or not prompt.strip():
            return Result.fail("Image prompt is invalid.")

        if parameters is not None and not isinstance(parameters, dict):
            return Result.fail("Gemini image parameters are invalid.")

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or not api_key.strip():
            return Result.fail("Gemini credentials are not configured.")

        resolved_model = _DEFAULT_MODEL
        config = self._build_config(parameters)

        try:
            if self._client is None:
                self._client = _create_gemini_client(api_key)

            response = self._client.models.generate_images(
                model=resolved_model,
                prompt=prompt.strip(),
                config=config,
            )
        except Exception:
            return Result.fail("Gemini image generation failed.")

        image_data = self._extract_image(response)
        if image_data is None:
            return Result.fail("Gemini returned no generated images.")

        image_bytes, mime_type = image_data
        fmt = _MIME_TO_FORMAT.get(mime_type, "PNG")
        ext = fmt.lower()
        if ext == "jpeg":
            ext = "jpg"

        try:
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(image_bytes))
            width, height = img.size

            output_dir = self._output_dir or tempfile.gettempdir()
            filename = f"gemini_{hash(prompt) & 0xFFFFFFFF:08x}.{ext}"
            output_path = os.path.join(output_dir, filename)
            img.save(output_path, format=fmt)
            img.close()
        except Exception:
            return Result.fail("Failed to process generated image.")

        return Result.ok(
            data={
                "path": output_path,
                "format": fmt,
                "width": width,
                "height": height,
                "provider": "gemini",
            },
            message="Image generated successfully.",
            metadata={
                "provider": "gemini",
                "model": resolved_model,
                "prompt": prompt.strip(),
            },
        )

    @staticmethod
    def _build_config(parameters: dict[str, Any] | None) -> Any:
        """Build GenerateImagesConfig from parameters dict."""
        if parameters is None:
            return None

        try:
            from google.genai import types
        except Exception:
            return None

        config_fields = {}
        field_map = {
            "negative_prompt": str,
            "number_of_images": int,
            "aspect_ratio": str,
            "guidance_scale": float,
            "seed": int,
            "output_mime_type": str,
            "output_compression_quality": int,
            "add_watermark": bool,
            "enhance_prompt": bool,
        }

        for key, expected_type in field_map.items():
            if key in parameters:
                val = parameters[key]
                if isinstance(val, expected_type):
                    config_fields[key] = val

        if not config_fields:
            return None

        try:
            return types.GenerateImagesConfig(**config_fields)
        except Exception:
            return None

    @staticmethod
    def _extract_image(response: Any) -> tuple[bytes, str] | None:
        """Extract image bytes and MIME type from response."""
        try:
            generated_images = response.generated_images
            if not generated_images:
                return None

            first = generated_images[0]
            image = first.image
            if image is None:
                return None

            image_bytes = image.image_bytes
            mime_type = image.mime_type or "image/png"

            if not isinstance(image_bytes, bytes) or not image_bytes:
                return None

            return image_bytes, mime_type
        except (AttributeError, IndexError, TypeError):
            return None
