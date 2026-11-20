from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from datetime import datetime
import enum


class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TaskStatus(str, enum.Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    result: Optional[str]
    error: Optional[str]


class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    result: Optional[str]
    error: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class PaginatedTasks(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[TaskRead]

    model_config = ConfigDict(from_attributes=True)
