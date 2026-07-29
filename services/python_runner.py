"""
services/python_runner.py

Python execution service.
"""

from __future__ import annotations

from pathlib import Path

from core.result import Result
from services.base_service import BaseService


class PythonRunner(BaseService):
    """
    High-level service responsible for executing Python code.

    This service delegates all execution to PythonTools.
    """

    def run_script(
        self,
        script_path: str | Path,
    ) -> Result:
        """
        Execute a Python script.
        """
        return self.python_tools.run_script(script_path)

    def run_module(
        self,
        module_name: str,
    ) -> Result:
        """
        Execute a Python module.
        """
        return self.python_tools.run_module(module_name)

    def run_code(
        self,
        code: str,
    ) -> Result:
        """
        Execute Python source code.
        """
        return self.python_tools.run_code(code)

    def python_version(self) -> Result:
        """
        Get Python version.
        """
        return self.python_tools.python_version()

    def python_executable(self) -> Result:
        """
        Get Python executable.
        """
        return self.python_tools.executable()