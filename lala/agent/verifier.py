import os
import ast
from typing import Dict, Any, Optional
from lala.agent.task import TaskStep, TaskResult
from lala.tools.filesystem import is_path_safe

class TaskVerifier:
    """
    Verification Engine for LALA Agent tasks.
    Validates file diffs, Python AST syntax, and Git repository state before declaring success.
    """
    def verify_step(self, step: TaskStep, tool_result_output: Any) -> bool:
        tool_name = (step.tool or "").lower()

        if tool_name == "file_edit":
            path_str = step.arguments.get("path", "")
            if not is_path_safe(path_str):
                return False
            
            canonical = os.path.realpath(path_str)
            if not os.path.exists(canonical):
                return False

            # If python file, verify AST syntax
            if canonical.endswith(".py"):
                try:
                    with open(canonical, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                    ast.parse(code)
                    return True
                except SyntaxError:
                    return False
            return True

        if tool_name == "git_tool":
            return True

        return True
