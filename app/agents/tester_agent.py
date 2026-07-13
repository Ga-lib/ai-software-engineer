"""
Tester Agent -- writes pytest unit tests for the generated code, informed by
the Reviewer Agent's notes so edge cases get covered, not just the happy path.
"""

import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.prompts.tester_prompt import TESTER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

settings = get_settings()


def get_tester_llm() -> ChatGroq:
    """Builds the LLM client used by the Tester Agent."""
    return ChatGroq(
        api_key=settings.groq_api_key,
        model="llama-3.3-70b-versatile",
        temperature=0.1,  # tests benefit from consistency, same reasoning as the Coding Agent
    )


async def run_tester_agent(generated_code: str, review_notes: str) -> str:
    """
    Runs the Tester Agent given the generated code and the Reviewer's notes.
    Returns the generated test code (including markdown fences) as plain text.
    """
    logger.info("Tester agent starting")

    llm = get_tester_llm()
    combined_input = (
        f"Generated code:\n{generated_code}\n\n"
        f"Review notes:\n{review_notes}"
    )
    messages = [
        SystemMessage(content=TESTER_SYSTEM_PROMPT),
        HumanMessage(content=combined_input),
    ]

    response = await llm.ainvoke(messages)
    test_code = response.content

    logger.info("Tester agent finished, produced %d characters", len(test_code))
    return test_code