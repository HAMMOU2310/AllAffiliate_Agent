from typing import Dict

from core.base_agent import BaseAgent


class AgentRegistry:
    """
    يحتفظ بجميع الوكلاء المسجلين داخل النظام.
    """

    def __init__(self):

        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):

        self._agents[agent.task_type] = agent

    def get(self, task_type: str):

        return self._agents.get(task_type)

    def list_agents(self):

        return list(self._agents.keys())