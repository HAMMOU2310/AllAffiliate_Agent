"""Offline WAV audio utilities for test fixtures and file validation.

This module provides deterministic audio-file operations using only the
Python standard library. It is NOT a TTS provider and must NOT be
presented as speech synthesis.

Use cases:
- Creating valid WAV test fixtures
- Validating WAV file structure
- Extracting duration and sample metadata
- Generating deterministic tone data for tests
"""

from __future__ import annotations

import io
import struct
import wave
from pathlib import Path
from typing import Any

from core.result import Result


def create_wav_file(
    path: str | Path,
    *,
    sample_rate: int = 16000,
    duration_seconds: float = 1.0,
    channels: int = 1,
    sample_width: int = 2,
    frequency: float = 440.0,
) -> Result:
    """Create a valid WAV file with a sine wave tone.

    This is a test fixture generator, NOT speech synthesis.
    """
    path = Path(path)
    try:
        num_samples = int(sample_rate * duration_seconds)
        max_val = (2 ** (sample_width * 8 - 1)) - 1

        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)

            frames = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                import math
                value = int(max_val * math.sin(2 * math.pi * frequency * t))
                frames.extend(struct.pack("<h", value))

            wf.writeframes(bytes(frames))

        return Result.ok(
            data={
                "path": str(path),
                "format": "wav",
                "sample_rate": sample_rate,
                "channels": channels,
                "sample_width": sample_width,
                "duration_seconds": duration_seconds,
                "frequency": frequency,
                "num_samples": num_samples,
            },
            message="WAV file created successfully.",
            metadata={"provider": "wav_fixture_generator"},
        )
    except Exception as exc:
        return Result.fail(f"WAV creation failed: {exc}")


def validate_wav_file(path: str | Path) -> Result:
    """Validate WAV file structure and return metadata."""
    path = Path(path)
    if not path.exists():
        return Result.fail(f"WAV file not found: {path}")
    if not path.is_file():
        return Result.fail(f"Path is not a file: {path}")

    try:
        with wave.open(str(path), "rb") as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            sample_rate = wf.getframerate()
            num_frames = wf.getnframes()
            duration = num_frames / sample_rate if sample_rate > 0 else 0.0

            return Result.ok(
                data={
                    "path": str(path),
                    "format": "wav",
                    "channels": channels,
                    "sample_width": sample_width,
                    "sample_rate": sample_rate,
                    "num_frames": num_frames,
                    "duration_seconds": round(duration, 4),
                    "valid": True,
                },
                message="WAV file is valid.",
                metadata={"provider": "wav_validator"},
            )
    except wave.Error as exc:
        return Result.fail(f"Invalid WAV file: {exc}")
    except Exception as exc:
        return Result.fail(f"WAV validation failed: {exc}")


def create_wav_bytes(
    *,
    sample_rate: int = 16000,
    duration_seconds: float = 1.0,
    channels: int = 1,
    sample_width: int = 2,
    frequency: float = 440.0,
) -> Result:
    """Create WAV audio data in memory (bytes). Returns bytes in data."""
    try:
        num_samples = int(sample_rate * duration_seconds)
        max_val = (2 ** (sample_width * 8 - 1)) - 1

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)

            frames = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                import math
                value = int(max_val * math.sin(2 * math.pi * frequency * t))
                frames.extend(struct.pack("<h", value))

            wf.writeframes(bytes(frames))

        wav_bytes = buf.getvalue()
        return Result.ok(
            data={
                "bytes": wav_bytes,
                "format": "wav",
                "sample_rate": sample_rate,
                "channels": channels,
                "sample_width": sample_width,
                "duration_seconds": duration_seconds,
                "frequency": frequency,
                "size_bytes": len(wav_bytes),
            },
            message="WAV bytes created successfully.",
            metadata={"provider": "wav_fixture_generator"},
        )
    except Exception as exc:
        return Result.fail(f"WAV bytes creation failed: {exc}")


def extract_wav_metadata(path: str | Path) -> dict[str, Any]:
    """Extract WAV metadata without validation Result wrapping."""
    path = Path(path)
    try:
        with wave.open(str(path), "rb") as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            sample_rate = wf.getframerate()
            num_frames = wf.getnframes()
            duration = num_frames / sample_rate if sample_rate > 0 else 0.0
            return {
                "path": str(path),
                "format": "wav",
                "channels": channels,
                "sample_width": sample_width,
                "sample_rate": sample_rate,
                "num_frames": num_frames,
                "duration_seconds": round(duration, 4),
            }
    except Exception:
        return {"path": str(path), "valid": False}
