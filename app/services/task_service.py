"""
Business logic for creating and retrieving tasks, and running the agent pipeline on them.
Routes call into this layer instead of talking to the database or agents directly.
"""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal
from app.graph.workflow import agent_graph
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate

logger = logging.getLogger(__name__)


async def create_task(db: AsyncSession, task_in: TaskCreate) -> Task:
    """Creates a new task row from a validated request and persists it."""
    task = Task(prompt=task_in.prompt)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    logger.info("Created task %s", task.id)
    return task


async def get_task(db: AsyncSession, task_id: uuid.UUID) -> Task | None:
    """Fetches a single task by its ID, or None if it doesn't exist."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def list_tasks(db: AsyncSession, limit: int = 50) -> list[Task]:
    """Fetches the most recent tasks, newest first."""
    result = await db.execute(
        select(Task).order_by(Task.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def run_agent_pipeline(task_id: uuid.UUID) -> None:
    """
    Runs the full LangGraph agent pipeline for a given task, then persists the result.

    This function opens its OWN database session since it runs as a background task,
    after the original request's session has already closed.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if task is None:
            logger.error("Pipeline could not find task %s", task_id)
            return

        try:
            task.status = TaskStatus.PLANNING
            await db.commit()
            logger.info("Task %s started via LangGraph pipeline", task_id)

            initial_state = {
                "task_id": str(task.id),
                "user_prompt": task.prompt,
                "plan": "",
                "research_notes": "",
                "generated_code": "",
                "review_notes": "",
                "test_results": "",
                "documentation": "",
                "error": "",
            }

            final_state = await agent_graph.ainvoke(initial_state)

            task.result = (
                f"## Plan\n{final_state['plan']}\n\n"
                f"## Research Notes\n{final_state['research_notes']}\n\n"
                f"## Generated Code\n{final_state['generated_code']}\n\n"
                f"## Review Notes\n{final_state['review_notes']}\n\n"
                f"## Generated Tests\n{final_state['test_results']}"
            )
            task.status = TaskStatus.COMPLETED
            await db.commit()
            logger.info("Task %s completed", task_id)

        except Exception as exc:  # noqa: BLE001 -- we want to catch any pipeline failure here
            logger.exception("Task %s failed during pipeline execution", task_id)
            task.status = TaskStatus.FAILED
            task.error_message = str(exc)
            await db.commit()