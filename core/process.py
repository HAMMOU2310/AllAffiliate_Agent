"""
core/process.py

Shared process execution utilities.

This module provides a unified way to execute external processes
and convert their results into the project's Result contract.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from core.result import Result


class ProcessRunner:
    """
    Execute external processes.

    All methods return Result.
    """

    def run(
        self,
        command: list[str],
        cwd: str | Path | None = None,
        timeout: int | None = None,
    ) -> Result:
        """
        Execute a command and return a Result object.
        """

        try:
            process = subprocess.run(
                command,
                cwd=Path(cwd) if cwd else None,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False,
            )

        except subprocess.TimeoutExpired as ex:
            return Result.fail(
                message="Process timed out.",
                errors=[str(ex)],
            )

        except FileNotFoundError as ex:
            return Result.fail(
                message="Executable not found.",
                errors=[str(ex)],
            )

        except Exception as ex:
            return Result.fail(
                message="Failed to execute process.",
                errors=[str(ex)],
            )

        metadata = {
            "command": command,
            "cwd": str(cwd) if cwd else None,
            "return_code": process.returncode,
            "stderr": process.stderr.strip(),
        }

        if process.returncode == 0:
            return Result.ok(
                data=process.stdout.strip(),
                message="Process executed successfully.",
                metadata=metadata,
            )

        return Result.fail(
            message="Process execution failed.",
            data=process.stdout.strip(),
            errors=[process.stderr.strip()],
            metadata=metadata,
        )