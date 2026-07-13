"""
Tests for the task service layer, particularly `run_agent_pipeline`.
The database and LangGraph agent calls are mocked so these tests are fast,
free, and don't depend on Supabase or Groq being reachable.
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models.task import Task, TaskStatus
from app.services import task_service


@pytest.mark.asyncio
async def test_run_agent_pipeline_marks_task_completed_on_success():
    """
    If the agent graph runs successfully, the task should end up COMPLETED
    with all structured fields populated from the graph's final state.
    """
    fake_task = Task(id=uuid4(), prompt="Write a hello world function")
    fake_task.status = TaskStatus.PENDING

    fake_final_state = {
        "plan": "1. Write function",
        "research_notes": "No special considerations",
        "generated_code": "```python\ndef hello(): return 'hi'\n```",
        "review_notes": "Looks correct",
        "test_results": "```python\ndef test_hello(): assert hello() == 'hi'\n```",
        "documentation": "## hello()\nReturns a greeting.",
    }

    mock_db_result = MagicMock()
    mock_db_result.scalar_one_or_none.return_value = fake_task

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_db_result

    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__.return_value = False

    with patch(
        "app.services.task_service.AsyncSessionLocal", return_value=mock_session_cm
    ), patch(
        "app.services.task_service.agent_graph.ainvoke",
        new=AsyncMock(return_value=fake_final_state),
    ):
        await task_service.run_agent_pipeline(fake_task.id)

    assert fake_task.status == TaskStatus.COMPLETED
    assert fake_task.plan == fake_final_state["plan"]
    assert fake_task.generated_code == fake_final_state["generated_code"]
    assert fake_task.documentation == fake_final_state["documentation"]
    assert fake_task.error_message is None


@pytest.mark.asyncio
async def test_run_agent_pipeline_marks_task_failed_on_exception():
    """
    If the agent graph raises an exception, the task should end up FAILED
    with the error message captured.
    """
    fake_task = Task(id=uuid4(), prompt="Write something that breaks")
    fake_task.status = TaskStatus.PENDING

    mock_db_result = MagicMock()
    mock_db_result.scalar_one_or_none.return_value = fake_task

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_db_result

    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__.return_value = False

    with patch(
        "app.services.task_service.AsyncSessionLocal", return_value=mock_session_cm
    ), patch(
        "app.services.task_service.agent_graph.ainvoke",
        new=AsyncMock(side_effect=RuntimeError("Groq API is down")),
    ):
        await task_service.run_agent_pipeline(fake_task.id)

    assert fake_task.status == TaskStatus.FAILED
    assert fake_task.error_message == "Groq API is down"


@pytest.mark.asyncio
async def test_run_agent_pipeline_handles_missing_task():
    """If the task_id doesn't correspond to a real row, the function should
    log an error and return without raising."""
    mock_db_result = MagicMock()
    mock_db_result.scalar_one_or_none.return_value = None

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_db_result

    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__.return_value = False

    with patch(
        "app.services.task_service.AsyncSessionLocal", return_value=mock_session_cm
    ):
        # Should not raise, even though no task was found.
        await task_service.run_agent_pipeline(uuid4())