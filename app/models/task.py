"""
Task model — represents a single user request being processed by the
multi-agent pipeline (Planner -> Research -> Coding -> Reviewer -> Tester -> Documentation).
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class TaskStatus(str, enum.Enum):
    """Possible states a task can be in as it moves through the agent pipeline."""

    PENDING = "pending"
    PLANNING = "planning"
    RESEARCHING = "researching"
    CODING = "coding"
    REVIEWING = "reviewing"
    TESTING = "testing"
    DOCUMENTING = "documenting"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(Base):
    """A single end-to-end request submitted by a user for the agents to handle."""

    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status"), default=TaskStatus.PENDING, nullable=False
    )
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Task id={self.id} status={self.status}>"