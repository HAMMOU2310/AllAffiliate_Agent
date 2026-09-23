"""
agents/master_agent.py

MasterAgent coordinates the complete execution pipeline.

Responsibilities:

- Receive user commands.
- Parse commands into Tasks.
- Retrieve execution context.
- Route Tasks to the appropriate Agent.
- Track execution context through MemoryAgent.
- Manage the execution session lifecycle.
- Receive Results.
- Display Results.

MasterAgent does not contain business logic.
"""

from __future__ import annotations

import uuid
from typing import Any

from rich.console import Console

from agents.memory_agent import MemoryAgent
from core.command_parser import CommandParser
from core.health import HealthChecker
from core.logger import Logger
from core.plugin_loader import PluginLoader
from core.plugin_registry import PluginRegistry
from core.result import Result
from core.router import TaskRouter
from core.service_container import ServiceContainer
from core.task import Task


class MasterAgent:
    """
    Main coordinator for the application execution pipeline.

    Each MasterAgent instance represents one execution session.
    Context information is stored through MemoryAgent.
    """

    def __init__(self):
        self.console = Console()

        self.services = ServiceContainer()
        self.parser = CommandParser()
        self.router = TaskRouter(self.services)

        self.memory_agent = self.router.registry.get("memory")

        self.health_checker = HealthChecker(self.services)

        workflow_service = self.services.get("workflow_service")
        if workflow_service is not None:
            workflow_service._router = self.router

        self.plugin_registry = PluginRegistry()
        self._load_plugins()

        self._shutdown_done = False

        self.session_id = ""
        self.start_session()

    def _load_plugins(self) -> None:
        """Discover and initialize plugins from the plugins/ directory."""
        loader = PluginLoader(
            plugins_dir="plugins",
            registry=self.plugin_registry,
        )
        loader.load_all(services=self.services, router=self.router)

    # ------------------------------------------------------------------
    # Session Lifecycle
    # ------------------------------------------------------------------

    def start_session(self) -> str:
        """
        Start a new execution session.

        Returns:
            The new session ID.
        """

        self.session_id = str(uuid.uuid4())

        return self.session_id

    def end_session(self) -> Result:
        """
        End the current execution session.

        Session and context memories belonging to the current session
        are cleared. Long-term memory is preserved by MemoryManager.
        ServiceContainer resources are released on final shutdown.
        """

        if self.memory_agent is None:
            return Result.fail(
                message="Memory Agent غير متاح."
            )

        if not self.session_id:
            return Result.fail(
                message="لا توجد جلسة نشطة."
            )

        task = Task(
            task_type="memory",
            command="clear_session",
            data={
                "operation": "clear_session",
                "session_id": self.session_id,
            },
        )

        result = self.memory_agent.execute(task)

        if result.success:
            self.session_id = ""

        return result

    def shutdown(self) -> None:
        """Release all application resources.

        Idempotent — safe to call multiple times.
        Clears session memory, shuts down plugins, then ServiceContainer.
        """
        if self._shutdown_done:
            return

        try:
            self.end_session()
        except Exception as exc:
            Logger.warning(f"Session cleanup failed during shutdown: {exc}")

        try:
            self.plugin_registry.shutdown_all()
        except Exception as exc:
            Logger.warning(f"Plugin shutdown failed: {exc}")

        try:
            self.services.shutdown()
        except Exception as exc:
            Logger.warning(f"ServiceContainer shutdown failed: {exc}")

        self._shutdown_done = True
        Logger.info("Application shutdown complete.")

    def health_check(self) -> Result:
        """Return system health status."""
        return self.health_checker.check()

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(self, command: str) -> Result:
        """
        Process one user command through the complete pipeline.

        The previous execution context is retrieved before routing
        the current task.

        The current command and execution result are then stored
        in context memory for the current session.
        """

        try:
            if not self.session_id:
                self.start_session()

            task = self.parser.parse(command)

            context = self._get_execution_context()

            if context:
                task.data["context"] = context

            self._save_context(
                key="last_command",
                value={
                    "command": command,
                    "task_type": task.task_type,
                    "task_data": task.data,
                },
            )

            result = self.router.route(task)

            self._save_context(
                key="last_result",
                value={
                    "success": result.success,
                    "message": result.message,
                    "data": result.data,
                    "errors": result.errors,
                },
            )

            return result

        except Exception as exc:
            Logger.error(f"خطأ غير متوقع في execute: {exc}")
            return Result.fail(
                message=f"حدث خطأ غير متوقع: {exc}",
                errors=[str(exc)],
            )

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    def _get_execution_context(self) -> dict[str, Any]:
        """
        Retrieve the execution context for the current session.

        The context consists of the previously stored command and
        result.

        Returns:
            A dictionary containing available context entries.
        """

        if self.memory_agent is None:
            return {}

        if not self.session_id:
            return {}

        context: dict[str, Any] = {}

        last_command = self.get_context("last_command")

        if last_command.success and last_command.data is not None:
            context["last_command"] = last_command.data

        last_result = self.get_context("last_result")

        if last_result.success and last_result.data is not None:
            context["last_result"] = last_result.data

        return context

    def _save_context(self, key: str, value: Any) -> None:
        """
        Save execution context through MemoryAgent.

        MemoryAgent remains responsible for memory operations.
        MasterAgent only coordinates the operation.
        """

        if self.memory_agent is None:
            return

        if not self.session_id:
            return

        task = Task(
            task_type="memory",
            command="save",
            data={
                "operation": "save",
                "memory_type": "context",
                "key": key,
                "value": value,
                "session_id": self.session_id,
            },
        )

        self.memory_agent.execute(task)

    def get_context(self, key: str) -> Result:
        """
        Retrieve one context memory entry from the current session.

        Returns:
            Result
        """

        if self.memory_agent is None:
            return Result.fail(
                message="Memory Agent غير متاح."
            )

        if not self.session_id:
            return Result.fail(
                message="لا توجد جلسة نشطة."
            )

        task = Task(
            task_type="memory",
            command="get",
            data={
                "operation": "get",
                "memory_type": "context",
                "key": key,
                "session_id": self.session_id,
            },
        )

        return self.memory_agent.execute(task)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def display_result(self, result: Result) -> None:
        """
        Display a Result to the user.
        """

        if result.message:
            self.console.print(result.message)

        if result.data is not None:
            self.console.print(result.data)

        if result.errors:
            for error in result.errors:
                self.console.print(error)

    # ------------------------------------------------------------------
    # Interactive Mode
    # ------------------------------------------------------------------

    def start(self) -> None:
        """
        Start the interactive command loop.
        """

        self.console.print()
        self.console.print(
            "[bold green]AllAffiliate_Agent جاهز للتنفيذ.[/bold green]"
        )
        self.console.print(
            "اكتب exit أو quit للخروج."
        )
        self.console.print()

        try:
            while True:
                try:
                    command = self.console.input(
                        "[bold cyan]>>> [/bold cyan]"
                    )

                except (EOFError, KeyboardInterrupt):
                    self.console.print()
                    break

                command = command.strip()

                if not command:
                    continue

                if command.lower() in {"exit", "quit"}:
                    break

                result = self.execute(command)

                self.display_result(result)

        finally:
            self.shutdown()