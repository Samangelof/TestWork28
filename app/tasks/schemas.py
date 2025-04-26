from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel


class TaskStatus(str, Enum):
    pending = "pending"
    done = "done"


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.pending
    priority: int = 0


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None


class TaskInDBBase(TaskBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class Task(TaskInDBBase):
    pass


class TaskSearchResults(BaseModel):
    results: List[Task]
    count: int