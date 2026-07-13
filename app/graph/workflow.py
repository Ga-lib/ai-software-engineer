"""
Builds the LangGraph workflow that orchestrates all agent nodes.
Currently: Planner -> Research -> Coding. More nodes are added here in later steps.
"""

from langgraph.graph import END, StateGraph

from app.graph.nodes import coding_node, planner_node, research_node
from app.graph.state import AgentState


def build_agent_graph():
    """
    Constructs and compiles the LangGraph workflow.

    Nodes: planner, research, coding
    Edges: START -> planner -> research -> coding -> END
    """
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("research", research_node)
    graph.add_node("coding", coding_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "research")
    graph.add_edge("research", "coding")
    graph.add_edge("coding", END)

    return graph.compile()


# Compiled once at import time and reused across requests — compiling is not free,
# and the graph structure never changes at runtime.
agent_graph = build_agent_graph()