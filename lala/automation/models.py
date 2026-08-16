from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class AutomationMode(str, Enum):
    SAFE = "SAFE"
    CONFIRM = "CONFIRM"
    MANUAL = "MANUAL"

class ActionClass(str, Enum):
    READ_ONLY = "READ_ONLY"
    ANALYSIS = "ANALYSIS"
    NETWORK_LOOKUP = "NETWORK_LOOKUP"
    LOCAL_MODIFICATION = "LOCAL_MODIFICATION"
    SECURITY_CONTROL = "SECURITY_CONTROL"
    DESTRUCTIVE = "DESTRUCTIVE"

class WorkflowState(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    WAITING_CONFIRMATION = "WAITING_CONFIRMATION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"
    TIMEOUT = "TIMEOUT"

class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    EXECUTED = "EXECUTED"

class ProposedAction(BaseModel):
    action: str
    target: str
    risk_class: ActionClass
    reason: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

class ApprovalRequest(BaseModel):
    approval_id: str
    case_id: str
    run_id: str
    action: str
    target: str
    risk: ActionClass
    reason: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: str
    confirmation_token: str
    status: ApprovalStatus = ApprovalStatus.PENDING

class WorkflowRun(BaseModel):
    run_id: str
    parent_run_id: Optional[str] = None
    case_id: str
    target: str
    mode: AutomationMode = AutomationMode.SAFE
    state: WorkflowState = WorkflowState.CREATED
    depth: int = 1
    action_count: int = 0
    retry_count: int = 0
    start_time: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    deadline: str
    executed_actions: List[Dict[str, Any]] = Field(default_factory=list)
    pending_approvals: List[ApprovalRequest] = Field(default_factory=list)

class AutomationConfig(BaseModel):
    mode: AutomationMode = AutomationMode.SAFE
    max_actions_per_run: int = 25
    max_runtime_seconds: int = 300
    max_case_evidence_items: int = 500
    max_workflow_depth: int = 8
    max_recovery_attempts: int = 2
    dry_run: bool = False
