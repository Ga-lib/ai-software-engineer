"""
Coding Agent — takes the plan and research notes and generates working Python code.
This is the output the Reviewer and Tester agents will operate on next.
"""

import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.prompts.coding_prompt import CODING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

settings = get_settings()


def get_coding_llm() -> ChatGroq:
    """Builds the LLM client used by the Coding Agent."""
    return ChatGroq(
        api_key=settings.groq_api_key,
        model="llama-3.3-70b-versatile",
        temperature=0.1,  # lower temperature: code generation benefits from consistency
    )


async def run_coding_agent(user_prompt: str, plan: str, research_notes: str) -> str:
    """
    Runs the Coding Agent given the original prompt, the plan, and research notes.
    Returns the generated code (including markdown fences) as plain text.
    """
    logger.info("Coding agent starting")

    llm = get_coding_llm()
    combined_input = (
        f"Original request:\n{user_prompt}\n\n"
        f"Plan from Planner Agent:\n{plan}\n\n"
        f"Research notes:\n{research_notes}"
    )
    messages = [
        SystemMessage(content=CODING_SYSTEM_PROMPT),
        HumanMessage(content=combined_input),
    ]

    response = await llm.ainvoke(messages)
    code_text = response.content

    logger.info("Coding agent finished, produced %d characters", len(code_text))
    return code_text