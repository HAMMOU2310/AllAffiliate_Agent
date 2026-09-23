"""Deterministic local image processing using Pillow."""

from __future__ import annotations

import os
from typing import Any

from core.result import Result


def _load_image(source: str) -> Any:
    """Load an image from a file path."""
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is unavailable.") from exc

    if not isinstance(source, str) or not source.strip():
        raise ValueError("Image source is invalid.")

    path = source.strip()
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Image file not found: {path}")

    try:
        return Image.open(path)
    except Exception as exc:
        raise ValueError(f"Cannot open image: {exc}") from exc


class LocalImageProvider:
    """Provider-owned local image processing operations."""

    _SUPPORTED_FORMATS = frozenset({
        "JPEG", "JPG", "PNG", "WEBP", "BMP", "GIF", "TIFF",
    })

    def process(
        self,
        source: str,
        operation: str,
        params: dict[str, Any] | None = None,
    ) -> Result:
        if not isinstance(source, str) or not source.strip():
            return Result.fail("Image source is invalid.")

        if not isinstance(operation, str) or not operation.strip():
            return Result.fail("Image operation is invalid.")

        op = operation.strip().lower()

        try:
            if op == "resize":
                return self._resize(source.strip(), params)
            elif op == "crop":
                return self._crop(source.strip(), params)
            elif op == "thumbnail":
                return self._thumbnail(source.strip(), params)
            elif op == "convert":
                return self._convert(source.strip(), params)
            elif op == "validate":
                return self._validate(source.strip())
            elif op == "metadata":
                return self._metadata(source.strip())
            else:
                return Result.fail(f"Unsupported operation: {op}")
        except FileNotFoundError as exc:
            return Result.fail(str(exc))
        except ValueError as exc:
            return Result.fail(str(exc))
        except Exception:
            return Result.fail(f"Image {op} failed.")

    def _resize(
        self, source: str, params: dict[str, Any] | None
    ) -> Result:
        if not params:
            return Result.fail("Resize requires width and height.")

        width = params.get("width")
        height = params.get("height")

        if not isinstance(width, int) or width <= 0:
            return Result.fail("Resize width is invalid.")
        if not isinstance(height, int) or height <= 0:
            return Result.fail("Resize height is invalid.")

        img = _load_image(source)
        resized = img.resize((width, height))
        output = self._output_path(source, f"resized_{width}x{height}")
        resized.save(output)
        img.close()

        return Result.ok(
            data={"path": output, "width": width, "height": height},
            message=f"Image resized to {width}x{height}.",
            metadata={"operation": "resize", "source": source},
        )

    def _crop(
        self, source: str, params: dict[str, Any] | None
    ) -> Result:
        if not params:
            return Result.fail("Crop requires x, y, width, and height.")

        x = params.get("x")
        y = params.get("y")
        width = params.get("width")
        height = params.get("height")

        for name, val in [("x", x), ("y", y), ("width", width), ("height", height)]:
            if not isinstance(val, int) or val < 0:
                return Result.fail(f"Crop {name} is invalid.")

        if width <= 0 or height <= 0:
            return Result.fail("Crop dimensions are invalid.")

        img = _load_image(source)
        cropped = img.crop((x, y, x + width, y + height))
        output = self._output_path(source, f"cropped_{width}x{height}")
        cropped.save(output)
        img.close()

        return Result.ok(
            data={"path": output, "width": width, "height": height},
            message=f"Image cropped to {width}x{height}.",
            metadata={"operation": "crop", "source": source},
        )

    def _thumbnail(
        self, source: str, params: dict[str, Any] | None
    ) -> Result:
        if not params or "size" not in params:
            return Result.fail("Thumbnail requires size.")

        size = params.get("size")
        if not isinstance(size, int) or size <= 0:
            return Result.fail("Thumbnail size is invalid.")

        img = _load_image(source)
        img.thumbnail((size, size))
        output = self._output_path(source, f"thumb_{size}")
        img.save(output)
        img.close()

        return Result.ok(
            data={"path": output, "size": size},
            message=f"Thumbnail created with max dimension {size}.",
            metadata={"operation": "thumbnail", "source": source},
        )

    def _convert(
        self, source: str, params: dict[str, Any] | None
    ) -> Result:
        if not params or "format" not in params:
            return Result.fail("Convert requires format.")

        fmt = params["format"].upper() if isinstance(params["format"], str) else ""
        if fmt not in self._SUPPORTED_FORMATS:
            return Result.fail(f"Unsupported format: {fmt}")

        img = _load_image(source)
        ext = "jpg" if fmt in ("JPEG", "JPG") else fmt.lower()
        output = self._output_path(source, f"converted.{ext}")
        pillow_fmt = "JPEG" if fmt == "JPG" else fmt
        img.save(output, format=pillow_fmt)
        img.close()

        return Result.ok(
            data={"path": output, "format": fmt},
            message=f"Image converted to {fmt}.",
            metadata={"operation": "convert", "source": source},
        )

    def _validate(self, source: str) -> Result:
        try:
            img = _load_image(source)
            width, height = img.size
            fmt = img.format or "UNKNOWN"
            img.close()

            return Result.ok(
                data={
                    "valid": True,
                    "width": width,
                    "height": height,
                    "format": fmt,
                },
                message="Image is valid.",
                metadata={"operation": "validate", "source": source},
            )
        except Exception as exc:
            return Result.ok(
                data={"valid": False, "error": str(exc)},
                message="Image validation failed.",
                metadata={"operation": "validate", "source": source},
            )

    def _metadata(self, source: str) -> Result:
        img = _load_image(source)
        width, height = img.size
        fmt = img.format or "UNKNOWN"
        mode = img.mode or "UNKNOWN"
        info = dict(img.info) if img.info else {}
        img.close()

        return Result.ok(
            data={
                "width": width,
                "height": height,
                "format": fmt,
                "mode": mode,
                "info": info,
            },
            message="Image metadata extracted.",
            metadata={"operation": "metadata", "source": source},
        )

    @staticmethod
    def _output_path(source: str, suffix: str) -> str:
        base, ext = os.path.splitext(source)
        return f"{base}_{suffix}{ext}"
