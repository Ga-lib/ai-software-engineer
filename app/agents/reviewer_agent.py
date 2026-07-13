"""
Reviewer Agent -- critically reviews the Coding Agent's output for bugs,
missed edge cases, and style issues before the Tester Agent runs.
"""

import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.prompts.reviewer_prompt import REVIEWER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

settings = get_settings()


def get_reviewer_llm() -> ChatGroq:
    """Builds the LLM client used by the Reviewer Agent."""
    return ChatGroq(
        api_key=settings.groq_api_key,
        model="llama-3.3-70b-versatile",
        temperature=0.2,
    )


async def run_reviewer_agent(plan: str, research_notes: str, generated_code: str) -> str:
    """
    Runs the Reviewer Agent given the plan, research notes, and generated code.
    Returns review notes as plain text.
    """
    logger.info("Reviewer agent starting")

    llm = get_reviewer_llm()
    combined_input = (
        f"Plan from Planner Agent:\n{plan}\n\n"
        f"Research notes:\n{research_notes}\n\n"
        f"Generated code:\n{generated_code}"
    )
    messages = [
        SystemMessage(content=REVIEWER_SYSTEM_PROMPT),
        HumanMessage(content=combined_input),
    ]

    response = await llm.ainvoke(messages)
    review_text = response.content

    logger.info("Reviewer agent finished, produced %d characters", len(review_text))
    return review_text