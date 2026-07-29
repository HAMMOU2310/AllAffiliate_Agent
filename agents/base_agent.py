"""
agents/base_agent.py
الفئة الأساسية لجميع الوكلاء التنفيذيين
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        دالة التنفيذ الرئيسية
        """
        pass