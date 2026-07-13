"""
Business logic for creating and retrieving tasks, and running the agent pipeline on them.
Routes call into this layer instead of talking to the database or agents directly.
"""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.planner_agent import run_planner_agent
from app.database.session import AsyncSessionLocal
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
    Runs the agent pipeline for a given task, updating its status and result as it goes.

    This function is designed to run as a FastAPI BackgroundTask, so it opens its OWN
    database session rather than reusing the one from the original request (which will
    already be closed by the time this runs).
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if task is None:
            logger.error("Pipeline could not find task %s", task_id)
            return

        try:
            # --- Planner stage ---
            task.status = TaskStatus.PLANNING
            await db.commit()
            logger.info("Task %s entered PLANNING stage", task_id)

            plan = await run_planner_agent(task.prompt)

            # For now, the plan IS the result. Later steps will append each
            # subsequent agent's output here instead of overwriting it.
            task.result = f"## Plan\n{plan}"
            task.status = TaskStatus.COMPLETED
            await db.commit()
            logger.info("Task %s completed", task_id)

        except Exception as exc:  # noqa: BLE001 -- we want to catch any agent failure here
            logger.exception("Task %s failed during pipeline execution", task_id)
            task.status = TaskStatus.FAILED
            task.error_message = str(exc)
            await db.commit()