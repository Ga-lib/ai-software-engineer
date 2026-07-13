"""
Tests for the Task Pydantic schemas -- validating request/response shape rules.
"""

import pytest
from pydantic import ValidationError

from app.schemas.task import TaskCreate


def test_task_create_accepts_valid_prompt():
    """A normal, non-empty prompt should be accepted."""
    task_in = TaskCreate(prompt="Build a calculator function")
    assert task_in.prompt == "Build a calculator function"


def test_task_create_rejects_empty_prompt():
    """An empty prompt should fail validation (min_length=1)."""
    with pytest.raises(ValidationError):
        TaskCreate(prompt="")


def test_task_create_rejects_overly_long_prompt():
    """A prompt over 5000 characters should fail validation (max_length=5000)."""
    with pytest.raises(ValidationError):
        TaskCreate(prompt="x" * 5001)