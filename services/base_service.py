"""
services/base_service.py

Base class for all services.
"""

from __future__ import annotations

from tools.file_tools import FileTools
from tools.python_tools import PythonTools
from tools.terminal_tools import TerminalTools


class BaseService:
    """
    Base class for all services.

    Provides access to the project's shared tools.
    """

    def __init__(
        self,
        file_tools: FileTools,
        terminal_tools: TerminalTools,
        python_tools: PythonTools,
    ) -> None:

        self.file_tools = file_tools
        self.terminal_tools = terminal_tools
        self.python_tools = python_tools