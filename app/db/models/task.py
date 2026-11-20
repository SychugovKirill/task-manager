from sqlalchemy import Column, Integer, String, Enum, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
import enum

Base = declarative_base()


class TaskPriority(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    def to_rabbitmq_priority(self) -> int:
        return {"LOW": 1, "MEDIUM": 5, "HIGH": 10}[self.value]


class TaskStatus(str, enum.Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Task(Base):
    __tablename__ = "tasks"

    def now_utc():
        return datetime.now(timezone.utc)

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus, name="taskstatus", create_type=False), nullable=False)

    created_at = Column(DateTime(timezone=True), default=now_utc)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
