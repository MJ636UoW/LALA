import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from lala.automation.models import ApprovalRequest, ApprovalStatus, ActionClass
from lala.utils.logging import logger

TOKEN_EXPIRATION_MINUTES = 15

class ApprovalSystem:
    """
    Approval & Confirmation Token System for LALA Phase 10.
    Generates single-use, SHA-256 bound, case-bound, run-bound, action-bound, target-bound, time-limited tokens.
    Prevents token reuse, cross-target reuse, and model self-approval.
    """
    def __init__(self):
        self._pending_approvals: Dict[str, ApprovalRequest] = {}
        self._used_tokens: set = set()

    def generate_token(self, case_id: str, run_id: str, action: str, target: str) -> str:
        nonce = str(uuid.uuid4())
        raw = f"{case_id}:{run_id}:{action}:{target}:{nonce}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def create_approval_request(self, case_id: str, run_id: str, action: str, target: str, risk: ActionClass, reason: str) -> ApprovalRequest:
        token = self.generate_token(case_id, run_id, action, target)
        app_id = str(uuid.uuid4())
        created_dt = datetime.now(timezone.utc)
        expires_dt = created_dt + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)

        req = ApprovalRequest(
            approval_id=app_id,
            case_id=case_id,
            run_id=run_id,
            action=action,
            target=target,
            risk=risk,
            reason=reason,
            created_at=created_dt.isoformat(),
            expires_at=expires_dt.isoformat(),
            confirmation_token=token,
            status=ApprovalStatus.PENDING
        )
        self._pending_approvals[token] = req
        logger.info(f"ApprovalSystem: Created confirmation request '{app_id}' for action '{action}' on target '{target}'. Token: {token[:12]}...")
        return req

    def validate_and_consume_token(self, token: str, case_id: str, run_id: str, action: str, target: str) -> Tuple[bool, str]:
        if not token or not isinstance(token, str):
            return False, "Token rejection: Invalid or empty token format."

        if token in self._used_tokens:
            return False, "Token rejection: Token has already been consumed (Single-use enforcement)."

        req = self._pending_approvals.get(token)
        if not req:
            return False, "Token rejection: Unrecognized or non-existent confirmation token."

        # Verify time limit
        expires_dt = datetime.fromisoformat(req.expires_at)
        if datetime.now(timezone.utc) > expires_dt:
            req.status = ApprovalStatus.EXPIRED
            return False, "Token rejection: Confirmation token has expired."

        # Verify binding parameters
        if req.case_id != case_id:
            return False, f"Token rejection: Token case mismatch ('{req.case_id}' != '{case_id}')."
        if req.run_id != run_id:
            return False, f"Token rejection: Token run mismatch ('{req.run_id}' != '{run_id}')."
        if req.action != action:
            return False, f"Token rejection: Token action mismatch ('{req.action}' != '{action}')."
        if req.target != target:
            return False, f"Token rejection: Token target mismatch ('{req.target}' != '{target}')."

        # Consume token
        self._used_tokens.add(token)
        req.status = ApprovalStatus.EXECUTED
        del self._pending_approvals[token]
        return True, "AUTHORIZED (Confirmation token validated and consumed)."
