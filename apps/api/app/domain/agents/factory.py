from app.core.agent.base import Agent
from app.domain.agents.butler import ButlerAgent
from app.domain.agents.subagent import SubAgentRunner


def create_agent(agent_type: str, name: str) -> Agent:
    if agent_type == "butler":
        return ButlerAgent(name=name)
    return SubAgentRunner(name=name)
