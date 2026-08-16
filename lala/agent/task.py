from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class TaskRisk(str, Enum):
    SAFE = "SAFE"
    READ_ONLY = "READ_ONLY"
    MODIFY = "MODIFY"
    DESTRUCTIVE = "DESTRUCTIVE"
    PRIVILEGED = "PRIVILEGED"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TaskStep(BaseModel):
    step_number: int
    action: str
    tool: Optional[str] = None
    arguments: Dict[str, Any] = Field(default_factory=dict)
    risk: TaskRisk = TaskRisk.READ_ONLY
    status: TaskStatus = TaskStatus.PENDING
    result_output: Optional[Any] = None
    error: Optional[str] = None

class TaskPlan(BaseModel):
    plan_id: str
    goal: str
    steps: List[TaskStep] = Field(default_factory=list)
    estimated_operations: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TaskResult(BaseModel):
    success: bool
    final_output: str
    steps_executed: int
    verification_passed: bool = False
    error: Optional[str] = None

class Task(BaseModel):
    task_id: str
    goal: str
    plan: Optional[TaskPlan] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
