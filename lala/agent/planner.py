import uuid
import json
import re
from typing import Optional, Dict, Any, List
from lala.agent.task import TaskPlan, TaskStep, TaskRisk, TaskStatus

SAFE_TOOLS = ["system_info", "workspace_scan"]
READ_ONLY_TOOLS = ["file_list", "file_read", "file_search", "python_analysis", "git_tool", "security_scan"]
MODIFY_TOOLS = ["file_edit"]

class TaskPlanner:
    """
    Structured Task Planner for LALA Phase 5.
    Generates structured risk-classified TaskPlan objects without executing tools directly.
    """
    def classify_risk(self, tool_name: str, arguments: Dict[str, Any]) -> TaskRisk:
        t_lower = tool_name.lower()
        if t_lower in SAFE_TOOLS:
            return TaskRisk.SAFE
        if t_lower in READ_ONLY_TOOLS:
            if t_lower == "git_tool":
                subcmd = arguments.get("subcommand", "status").lower()
                if subcmd in ["add", "commit", "push", "checkout", "reset"]:
                    return TaskRisk.MODIFY
            return TaskRisk.READ_ONLY
        if t_lower in MODIFY_TOOLS:
            return TaskRisk.MODIFY
        if "delete" in t_lower or "reset" in t_lower:
            return TaskRisk.DESTRUCTIVE
        if "shell" in t_lower or "privileged" in t_lower:
            return TaskRisk.PRIVILEGED
        return TaskRisk.READ_ONLY

    def create_plan_for_goal(self, goal: str, raw_plan_json: Optional[str] = None) -> TaskPlan:
        steps: List[TaskStep] = []

        if raw_plan_json:
            try:
                match = re.search(r'```json\s*(\{.*?\})\s*```', raw_plan_json, re.DOTALL)
                json_str = match.group(1) if match else raw_plan_json
                data = json.loads(json_str)
                for idx, step_data in enumerate(data.get("steps", []), start=1):
                    tool_name = step_data.get("tool", step_data.get("action", ""))
                    args = step_data.get("arguments", {})
                    risk = self.classify_risk(tool_name, args)
                    steps.append(TaskStep(
                        step_number=idx,
                        action=step_data.get("action", f"Execute {tool_name}"),
                        tool=tool_name,
                        arguments=args,
                        risk=risk
                    ))
            except Exception:
                pass

        # Fallback structured default plan if parsing raw JSON fails or for standard analysis goals
        if not steps:
            goal_lower = goal.lower()
            if "security" in goal_lower or "analyze" in goal_lower:
                steps = [
                    TaskStep(step_number=1, action="Scan Workspace", tool="workspace_scan", risk=TaskRisk.SAFE),
                    TaskStep(step_number=2, action="Run Security Scanner", tool="security_scan", risk=TaskRisk.READ_ONLY),
                    TaskStep(step_number=3, action="Analyze Code AST", tool="python_analysis", risk=TaskRisk.READ_ONLY),
                    TaskStep(step_number=4, action="Summarize Findings", tool="system_info", risk=TaskRisk.SAFE)
                ]
            else:
                steps = [
                    TaskStep(step_number=1, action="Scan Workspace", tool="workspace_scan", risk=TaskRisk.SAFE),
                    TaskStep(step_number=2, action="Inspect Files", tool="file_list", risk=TaskRisk.READ_ONLY)
                ]

        return TaskPlan(
            plan_id=str(uuid.uuid4()),
            goal=goal,
            steps=steps,
            estimated_operations=len(steps)
        )
