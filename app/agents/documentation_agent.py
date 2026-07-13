"""
Documentation Agent -- writes developer-facing documentation for the generated
code and tests. This is the final agent in the pipeline.
"""

import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.prompts.documentation_prompt import DOCUMENTATION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

settings = get_settings()


def get_documentation_llm() -> ChatGroq:
    """Builds the LLM client used by the Documentation Agent."""
    return ChatGroq(
        api_key=settings.groq_api_key,
        model="llama-3.3-70b-versatile",
        temperature=0.3,
    )


async def run_documentation_agent(
    user_prompt: str, generated_code: str, test_results: str
) -> str:
    """
    Runs the Documentation Agent given the original request, generated code, and tests.
    Returns the generated documentation as Markdown text.
    """
    logger.info("Documentation agent starting")

    llm = get_documentation_llm()
    combined_input = (
        f"Original request:\n{user_prompt}\n\n"
        f"Generated code:\n{generated_code}\n\n"
        f"Generated tests:\n{test_results}"
    )
    messages = [
        SystemMessage(content=DOCUMENTATION_SYSTEM_PROMPT),
        HumanMessage(content=combined_input),
    ]

    response = await llm.ainvoke(messages)
    documentation_text = response.content

    logger.info("Documentation agent finished, produced %d characters", len(documentation_text))
    return documentation_text