"""
Shared state object that flows through the LangGraph pipeline.
Every agent node reads from and writes to this same state, so each agent
has access to everything produced by the agents that ran before it.
"""

from typing import TypedDict


class AgentState(TypedDict):
    """
    The data that flows between nodes in the agent graph.

    Fields are added to incrementally as each agent runs — e.g. `plan` is empty
    until the Planner node runs, then stays populated for every node after it.
    """

    task_id: str
    user_prompt: str

    plan: str
    research_notes: str

    # Populated by agents we haven't built yet — reserved now so the state
    # shape is stable as we add nodes in later steps.
    generated_code: str
    review_notes: str
    test_results: str
    documentation: str

    error: str