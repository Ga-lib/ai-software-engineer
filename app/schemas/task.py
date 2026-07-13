"""
Pydantic schemas for the Task API.
These define what data the API accepts (requests) and returns (responses),
kept separate from the SQLAlchemy database model.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    """Shape of the data required to create a new task."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The user's request for the AI agent pipeline to process.",
    )


class TaskRead(BaseModel):
    """Shape of the data returned to the client when reading a task."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    prompt: str
    status: TaskStatus
    result: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime