"""
LangGraph node functions. Each node wraps one agent, reading what it needs from
the shared AgentState and writing its output back into that same state.
"""

import logging

from app.agents.coding_agent import run_coding_agent
from app.agents.planner_agent import run_planner_agent
from app.agents.research_agent import run_research_agent
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def planner_node(state: AgentState) -> dict:
    """Runs the Planner Agent and writes its output into state['plan']."""
    logger.info("Graph: running planner_node for task %s", state["task_id"])
    plan = await run_planner_agent(state["user_prompt"])
    return {"plan": plan}


async def research_node(state: AgentState) -> dict:
    """Runs the Research Agent and writes its output into state['research_notes']."""
    logger.info("Graph: running research_node for task %s", state["task_id"])
    research_notes = await run_research_agent(state["user_prompt"], state["plan"])
    return {"research_notes": research_notes}


async def coding_node(state: AgentState) -> dict:
    """Runs the Coding Agent and writes its output into state['generated_code']."""
    logger.info("Graph: running coding_node for task %s", state["task_id"])
    generated_code = await run_coding_agent(
        state["user_prompt"], state["plan"], state["research_notes"]
    )
    return {"generated_code": generated_code}