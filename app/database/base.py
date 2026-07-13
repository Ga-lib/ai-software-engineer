"""
Declarative base class for all SQLAlchemy ORM models.
Every table model in app/models/ will inherit from this Base.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models in the project."""

    pass