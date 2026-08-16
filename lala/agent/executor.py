from typing import Optional, Dict, Any
from lala.agent.task import TaskPlan, TaskStep, TaskResult, TaskStatus, TaskRisk
from lala.agent.planner import TaskPlanner
from lala.agent.verifier import TaskVerifier
from lala.agent.recovery import TaskRecoveryManager
from lala.tools.executor import ToolExecutor
from lala.tools.planner import ToolCallRequest
from lala.utils.logging import logger

MAX_AGENT_STEPS = 8

class AgentExecutor:
    """
    Multi-Step Agent Executor for LALA Phase 5.
    Drives task step execution bounded strictly by MAX_AGENT_STEPS = 8.
    Verifies step outcomes via TaskVerifier and handles safe retries via TaskRecoveryManager.
    """
    def __init__(self, executor: Optional[ToolExecutor] = None):
        self.executor = executor or ToolExecutor()
        self.verifier = TaskVerifier()
        self.recovery = TaskRecoveryManager()

    def execute_plan(self, plan: TaskPlan) -> TaskResult:
        steps_executed = 0
        outputs = []

        for step in plan.steps[:MAX_AGENT_STEPS]:
            steps_executed += 1
            step.status = TaskStatus.IN_PROGRESS
            logger.info(f"Agent Execution Step {step.step_number}/{len(plan.steps)}: {step.action} (Risk: {step.risk.value})")

            # Route step tool execution
            if step.tool:
                req = ToolCallRequest(tool=step.tool, arguments=step.arguments, reason=step.action, risk=step.risk.value)
                res = self.executor.execute_request(req)

                if res.success:
                    # Verify result
                    verified = self.verifier.verify_step(step, res.output)
                    if verified:
                        step.status = TaskStatus.COMPLETED
                        step.result_output = res.output
                        outputs.append(f"Step {step.step_number} [{step.action}]: Success ({res.output})")
                    else:
                        step.status = TaskStatus.FAILED
                        step.error = "Verification Failed"
                        outputs.append(f"Step {step.step_number} [{step.action}]: Verification Failed")
                        break
                else:
                    # Check recovery
                    if self.recovery.should_retry(step, res.error or ""):
                        retry_res = self.executor.execute_request(req)
                        if retry_res.success:
                            step.status = TaskStatus.COMPLETED
                            step.result_output = retry_res.output
                            outputs.append(f"Step {step.step_number} [{step.action}]: Retry Success ({retry_res.output})")
                            continue

                    step.status = TaskStatus.FAILED
                    step.error = res.error
                    outputs.append(f"Step {step.step_number} [{step.action}]: Failed - {res.error}")
                    return TaskResult(
                        success=False,
                        final_output="\n".join(outputs),
                        steps_executed=steps_executed,
                        verification_passed=False,
                        error=res.error
                    )
            else:
                step.status = TaskStatus.COMPLETED
                outputs.append(f"Step {step.step_number} [{step.action}]: Completed")

        return TaskResult(
            success=True,
            final_output="\n".join(outputs),
            steps_executed=steps_executed,
            verification_passed=True
        )
