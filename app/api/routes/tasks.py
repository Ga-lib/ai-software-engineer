"""
API routes for creating and retrieving tasks.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.task import TaskCreate, TaskRead
from app.services import task_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate, db: AsyncSession = Depends(get_db)
) -> TaskRead:
    """Submits a new request for the AI agent pipeline to process."""
    task = await task_service.create_task(db, task_in)
    return task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> TaskRead:
    """Fetches the current status/result of a single task by ID."""
    task = await task_service.get_task(db, task_id)
    if task is None:
        logger.warning("Task %s not found", task_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.get("", response_model=list[TaskRead])
async def list_tasks(db: AsyncSession = Depends(get_db)) -> list[TaskRead]:
    """Lists the most recent tasks, newest first."""
    return await task_service.list_tasks(db)