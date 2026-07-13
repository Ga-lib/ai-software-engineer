"""
Planner Agent — takes a user's raw request and produces an ordered list of subtasks.
This is the first agent in the pipeline; its output feeds the Research and Coding agents.
"""

import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.prompts.planner_prompt import PLANNER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

settings = get_settings()


def get_planner_llm() -> ChatGroq:
    """
    Builds the LLM client used by the Planner Agent.
    Kept as its own function so it's easy to swap the model later.
    """
    return ChatGroq(
        api_key=settings.groq_api_key,
        model="llama-3.3-70b-versatile",
        temperature=0.2,  # low temperature: we want consistent, structured plans, not creativity
    )


async def run_planner_agent(user_prompt: str) -> str:
    """
    Runs the Planner Agent on a user's request and returns the generated plan as plain text.
    """
    logger.info("Planner agent starting for prompt: %s", user_prompt[:100])

    llm = get_planner_llm()
    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    response = await llm.ainvoke(messages)
    plan_text = response.content

    logger.info("Planner agent finished, produced %d characters", len(plan_text))
    return plan_text