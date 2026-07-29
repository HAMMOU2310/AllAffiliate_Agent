"""
tools/terminal_tools.py

Execute terminal commands safely.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from core.result import Result


class TerminalTools:
    """
    Execute terminal commands.

    All methods return Result.
    """

    def run(
        self,
        command: list[str],
        cwd: str | Path | None = None,
        timeout: int | None = None,
    ) -> Result:

        try:
            process = subprocess.run(
                command,
                cwd=Path(cwd) if cwd else None,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False,
            )

            return Result.ok(
                data=process.stdout.strip(),
                message="Command executed successfully.",
                metadata={
                    "stderr": process.stderr.strip(),
                    "return_code": process.returncode,
                    "command": command,
                    "cwd": str(cwd) if cwd else None,
                },
            )

        except Exception as ex:
            return Result.fail(
                message="Command execution failed.",
                errors=[str(ex)],
            )

    def run_powershell(
        self,
        command: str,
        cwd: str | Path | None = None,
        timeout: int | None = None,
    ) -> Result:

        return self.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                command,
            ],
            cwd,
            timeout,
        )

    def run_cmd(
        self,
        command: str,
        cwd: str | Path | None = None,
        timeout: int | None = None,
    ) -> Result:

        return self.run(
            [
                "cmd",
                "/c",
                command,
            ],
            cwd,
            timeout,
        )

    def command_exists(
        self,
        command: str,
    ) -> Result:

        try:
            exists = shutil.which(command) is not None

            return Result.ok(
                data=exists,
                message="Command checked successfully.",
            )

        except Exception as ex:
            return Result.fail(
                message="Failed to check command.",
                errors=[str(ex)],
            )

    def current_directory(self) -> Result:

        try:
            return Result.ok(
                data=Path.cwd(),
                message="Current directory retrieved.",
            )

        except Exception as ex:
            return Result.fail(
                message="Failed to get current directory.",
                errors=[str(ex)],
            )