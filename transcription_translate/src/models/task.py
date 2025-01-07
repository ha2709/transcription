import uuid

from sqlalchemy import Column, DateTime, Integer, Sequence, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from src.models.base import Base


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(
        String,
        primary_key=True,
        unique=True,
        index=True,
    )

    status = Column(
        String, default="pending"
    )  # Task status (e.g., pending, processing, completed)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    translated_text = Column(
        String, nullable=True
    )  # URL for output file (if applicable)
    user_ip = Column(
        String, nullable=False
    )  # Reference to the user who uploaded the task

    def __repr__(self):
        return f"<Task(task_id={self.task_id}, status={self.status})>"
