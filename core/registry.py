"""
core/registry.py

Central registry for all Agents in the system.

Responsibilities:

- Register Agents.
- Prevent duplicate task types.
- Retrieve Agents by task type.
- List registered Agents.

AgentRegistry does not execute Agents.
"""

from typing import Dict

from core.base_agent import BaseAgent


class AgentRegistry:
    """
    Maintains all registered Agents inside the system.

    Each Agent is identified by its task_type.

    Duplicate task types are rejected to prevent accidental
    replacement of an already registered Agent.
    """

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, agent: BaseAgent) -> None:
        """
        Register an Agent.

        Raises:
            TypeError:
                If the provided object is not a BaseAgent.

            ValueError:
                If the Agent has an empty task_type.

            ValueError:
                If another Agent is already registered
                with the same task_type.
        """

        if not isinstance(agent, BaseAgent):
            raise TypeError(
                "Agent must be an instance of BaseAgent."
            )

        task_type = agent.task_type

        if not isinstance(task_type, str) or not task_type.strip():
            raise ValueError(
                "Agent task_type cannot be empty."
            )

        task_type = task_type.strip()

        if task_type in self._agents:
            existing_agent = self._agents[task_type]

            raise ValueError(
                f"Agent task_type '{task_type}' is already registered "
                f"by '{existing_agent.name}'."
            )

        self._agents[task_type] = agent

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get(self, task_type: str):
        """
        Retrieve an Agent by task_type.

        Returns:
            The registered Agent, or None if not found.
        """

        return self._agents.get(task_type)

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def list_agents(self) -> list[str]:
        """
        Return all registered task types.
        """

        return list(self._agents.keys())