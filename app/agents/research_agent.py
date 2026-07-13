"""
Research Agent — takes the Planner's output and gathers relevant technical context
(best practices, libraries, edge cases) before the Coding Agent implements anything.
"""

import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.prompts.research_prompt import RESEARCH_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

settings = get_settings()


def get_research_llm() -> ChatGroq:
    """Builds the LLM client used by the Research Agent."""
    return ChatGroq(
        api_key=settings.groq_api_key,
        model="llama-3.3-70b-versatile",
        temperature=0.3,
    )


async def run_research_agent(user_prompt: str, plan: str) -> str:
    """
    Runs the Research Agent given the original user prompt and the Planner's plan.
    Returns research notes as plain text.
    """
    logger.info("Research agent starting")

    llm = get_research_llm()
    combined_input = (
        f"Original request:\n{user_prompt}\n\n"
        f"Plan from Planner Agent:\n{plan}"
    )
    messages = [
        SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
        HumanMessage(content=combined_input),
    ]

    response = await llm.ainvoke(messages)
    research_text = response.content

    logger.info("Research agent finished, produced %d characters", len(research_text))
    return research_text