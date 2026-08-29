from abc import ABC, abstractmethod

from core.result import Result


class BaseAgent(ABC):
    name = "BaseAgent"
    task_type = "base"

    @abstractmethod
    def execute(self, task) -> Result:
        raise NotImplementedError