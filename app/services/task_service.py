"""
Business logic for creating and retrieving tasks.
Routes call into this layer instead of talking to the database directly.
"""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
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