"""
Builds the LangGraph workflow that orchestrates all agent nodes.
Full pipeline: Planner -> Research -> Coding -> Reviewer -> Tester -> Documentation.
"""

from langgraph.graph import END, StateGraph

from app.graph.nodes import (
    coding_node,
    documentation_node,
    planner_node,
    research_node,
    reviewer_node,
    tester_node,
)
from app.graph.state import AgentState


def build_agent_graph():
    """
    Constructs and compiles the LangGraph workflow.

    Nodes: planner, research, coding, reviewer, tester, documentation
    Edges: START -> planner -> research -> coding -> reviewer -> tester -> documentation -> END
    """
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("research", research_node)
    graph.add_node("coding", coding_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("tester", tester_node)
    graph.add_node("documentation", documentation_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "research")
    graph.add_edge("research", "coding")
    graph.add_edge("coding", "reviewer")
    graph.add_edge("reviewer", "tester")
    graph.add_edge("tester", "documentation")
    graph.add_edge("documentation", END)

    return graph.compile()


# Compiled once at import time and reused across requests -- compiling is not free,
# and the graph structure never changes at runtime.
agent_graph = build_agent_graph()