from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from pydantic import BaseModel

class SubagentResult(BaseModel):
    agent_id: str
    status: str
    output: str

class BaseSubagent(ABC):
    """
    Abstract Base Subagent interface for task delegation.
    Autonomous execution deferred to later phases.
    """
    def __init__(self, agent_id: str, role: str):
        self.agent_id = agent_id
        self.role = role

    @abstractmethod
    def run_task(self, task_description: str) -> SubagentResult:
        pass

class SubagentManager:
    """
    Manager abstraction for orchestrating subagents.
    """
    def __init__(self):
        self._subagents: Dict[str, BaseSubagent] = {}

    def register_subagent(self, agent: BaseSubagent):
        self._subagents[agent.agent_id] = agent

    def get_subagent(self, agent_id: str) -> Optional[BaseSubagent]:
        return self._subagents.get(agent_id)

    def list_subagents(self) -> List[str]:
        return list(self._subagents.keys())
