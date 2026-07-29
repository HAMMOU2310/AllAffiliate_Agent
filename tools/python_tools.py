"""
tools/python_tools.py

Utilities for executing Python commands.
"""

from __future__ import annotations

import sys
from pathlib import Path

from core.process import ProcessRunner
from core.result import Result


class PythonTools:
    """
    Execute Python scripts, modules and code.

    All methods return Result.
    """

    def __init__(self) -> None:
        self._runner = ProcessRunner()

    def run_script(
        self,
        script: str | Path,
        *args: str,
        cwd: str | Path | None = None,
        timeout: int | None = None,
    ) -> Result:
        """
        Execute a Python script.
        """

        return self._runner.run(
            command=[
                sys.executable,
                str(Path(script)),
                *args,
            ],
            cwd=cwd,
            timeout=timeout,
        )

    def run_module(
        self,
        module: str,
        *args: str,
        cwd: str | Path | None = None,
        timeout: int | None = None,
    ) -> Result:
        """
        Execute a Python module.
        """

        return self._runner.run(
            command=[
                sys.executable,
                "-m",
                module,
                *args,
            ],
            cwd=cwd,
            timeout=timeout,
        )

    def run_code(
        self,
        code: str,
        timeout: int | None = None,
    ) -> Result:
        """
        Execute Python source code.
        """

        return self._runner.run(
            command=[
                sys.executable,
                "-c",
                code,
            ],
            timeout=timeout,
        )

    def python_version(self) -> Result:
        """
        Get Python version.
        """

        return self._runner.run(
            command=[
                sys.executable,
                "--version",
            ],
        )

    def executable(self) -> Result:
        """
        Get Python executable.
        """

        return Result.ok(
            data=sys.executable,
            message="Python executable retrieved successfully.",
        )