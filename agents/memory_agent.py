"""
agents/memory_agent.py

Agent responsible for coordinating memory-related tasks.

The MemoryAgent does not contain memory storage logic.
All memory operations are delegated to MemoryManager.
"""

from __future__ import annotations

from core.base_agent import BaseAgent
from core.result import Result
from memory.memory_manager import MemoryManager


class MemoryAgent(BaseAgent):
    """
    Agent responsible for memory-related tasks.
    """

    name = "Memory Agent"
    task_type = "memory"

    def __init__(
        self,
        memory_manager: MemoryManager | None = None,
    ) -> None:
        self.memory_manager = memory_manager

    def execute(self, task) -> Result:
        """
        Execute a memory-related task.

        Supported operations are provided through task.data:

            save
            get
            get_entry
            search
            list
            delete
            clear_session
            count
            health_check
        """

        if self.memory_manager is None:
            return Result.fail(
                message="MemoryManager غير متاح."
            )

        try:
            operation = task.data.get("operation")

            if not operation:
                return Result.fail(
                    message="لم يتم تحديد عملية الذاكرة."
                )

            if operation == "save":
                return self._save(task)

            if operation == "get":
                return self._get(task)

            if operation == "get_entry":
                return self._get_entry(task)

            if operation == "search":
                return self._search(task)

            if operation == "list":
                return self._list(task)

            if operation == "delete":
                return self._delete(task)

            if operation == "clear_session":
                return self._clear_session(task)

            if operation == "count":
                return self._count(task)

            if operation == "health_check":
                return self._health_check()

            return Result.fail(
                message=f"عملية الذاكرة غير مدعومة: {operation}"
            )

        except Exception as exc:
            return Result.fail(
                message=str(exc)
            )

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _save(self, task) -> Result:
        data = task.data

        memory_type = data.get("memory_type")
        key = data.get("key")

        if not memory_type:
            return Result.fail(
                message="memory_type مطلوب."
            )

        if not key:
            return Result.fail(
                message="key مطلوب."
            )

        memory_id = self.memory_manager.save(
            memory_type=memory_type,
            key=key,
            value=data.get("value"),
            session_id=data.get("session_id"),
            metadata=data.get("metadata"),
        )

        return Result.ok(
            data={
                "id": memory_id,
            },
            message="تم حفظ الذاكرة بنجاح.",
        )

    # ------------------------------------------------------------------
    # Get
    # ------------------------------------------------------------------

    def _get(self, task) -> Result:
        data = task.data

        memory_type = data.get("memory_type")
        key = data.get("key")

        if not memory_type:
            return Result.fail(
                message="memory_type مطلوب."
            )

        if not key:
            return Result.fail(
                message="key مطلوب."
            )

        value = self.memory_manager.get(
            memory_type=memory_type,
            key=key,
            session_id=data.get("session_id"),
        )

        if value is None:
            return Result.ok(
                data=None,
                message="لم يتم العثور على الذاكرة.",
            )

        return Result.ok(
            data=value,
            message="تم استرجاع الذاكرة.",
        )

    # ------------------------------------------------------------------
    # Get Entry
    # ------------------------------------------------------------------

    def _get_entry(self, task) -> Result:
        data = task.data

        memory_type = data.get("memory_type")
        key = data.get("key")

        if not memory_type:
            return Result.fail(
                message="memory_type مطلوب."
            )

        if not key:
            return Result.fail(
                message="key مطلوب."
            )

        entry = self.memory_manager.get_entry(
            memory_type=memory_type,
            key=key,
            session_id=data.get("session_id"),
        )

        if entry is None:
            return Result.ok(
                data=None,
                message="لم يتم العثور على الذاكرة.",
            )

        return Result.ok(
            data=entry,
            message="تم استرجاع سجل الذاكرة.",
        )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def _search(self, task) -> Result:
        data = task.data

        query = data.get("query", "")

        results = self.memory_manager.search(
            query=query,
            memory_type=data.get("memory_type"),
            session_id=data.get("session_id"),
            limit=data.get("limit", 20),
        )

        return Result.ok(
            data=results,
            message="تم البحث في الذاكرة.",
        )

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    def _list(self, task) -> Result:
        data = task.data

        results = self.memory_manager.list_memories(
            memory_type=data.get("memory_type"),
            session_id=data.get("session_id"),
            limit=data.get("limit", 100),
        )

        return Result.ok(
            data=results,
            message="تم جلب الذاكرة.",
        )

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def _delete(self, task) -> Result:
        data = task.data

        memory_type = data.get("memory_type")
        key = data.get("key")

        if not memory_type:
            return Result.fail(
                message="memory_type مطلوب."
            )

        if not key:
            return Result.fail(
                message="key مطلوب."
            )

        deleted = self.memory_manager.delete(
            memory_type=memory_type,
            key=key,
            session_id=data.get("session_id"),
        )

        if not deleted:
            return Result.ok(
                data=False,
                message="لم يتم العثور على الذاكرة.",
            )

        return Result.ok(
            data=True,
            message="تم حذف الذاكرة.",
        )

    # ------------------------------------------------------------------
    # Clear Session
    # ------------------------------------------------------------------

    def _clear_session(self, task) -> Result:
        session_id = task.data.get("session_id")

        if not session_id:
            return Result.fail(
                message="session_id مطلوب."
            )

        deleted_count = self.memory_manager.clear_session(
            session_id=session_id,
        )

        return Result.ok(
            data={
                "deleted_count": deleted_count,
            },
            message="تم تنظيف ذاكرة الجلسة.",
        )

    # ------------------------------------------------------------------
    # Count
    # ------------------------------------------------------------------

    def _count(self, task) -> Result:
        data = task.data

        count = self.memory_manager.count(
            memory_type=data.get("memory_type"),
            session_id=data.get("session_id"),
        )

        return Result.ok(
            data=count,
            message="تم حساب عدد عناصر الذاكرة.",
        )

    # ------------------------------------------------------------------
    # Health Check
    # ------------------------------------------------------------------

    def _health_check(self) -> Result:
        healthy = self.memory_manager.health_check()

        if not healthy:
            return Result.fail(
                message="Memory System غير متاح."
            )

        return Result.ok(
            data=True,
            message="Memory System يعمل بشكل صحيح.",
        )