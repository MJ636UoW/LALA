import ast
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel

BLOCKED_AST_NODES = ["Import", "ImportFrom", "Call"]
BLOCKED_CALLS = ["eval", "exec", "os.system", "subprocess", "socket", "open", "__import__"]

class PythonAnalysisTool(Tool):
    """
    Controlled Python code static analysis and safe AST parsing tool.
    Blocks arbitrary shell execution and dangerous imports.
    """
    def __init__(self):
        super().__init__(
            name="python_analysis",
            description="Parse Python code AST, analyze structure, and calculate safe math expressions.",
            category="analysis",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="Safe AST analysis and evaluation"
        )

    def execute(self, **kwargs) -> ToolResult:
        code = kwargs.get("code", "")
        if not code.strip():
            return ToolResult(success=False, output=None, error="No code provided for analysis.")

        # Check for blocked calls in text
        for blocked in BLOCKED_CALLS:
            if blocked in code:
                return ToolResult(success=False, output=None, error=f"Security Restriction: Use of '{blocked}' is strictly blocked in PythonAnalysisTool.")

        try:
            tree = ast.parse(code)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            # Safe math evaluation if expression
            eval_res = None
            if len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr):
                try:
                    eval_res = eval(compile(tree, filename="<ast>", mode="eval"), {"__builtins__": {}})
                except Exception:
                    pass

            return ToolResult(success=True, output={
                "valid_syntax": True,
                "functions_found": functions,
                "classes_found": classes,
                "expression_result": eval_res
            })
        except SyntaxError as se:
            return ToolResult(success=False, output=None, error=f"Syntax Error in Python code: {se}")
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
