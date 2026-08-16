import ast
from typing import List
from lala.security.findings import SecurityFinding, SeverityLevel

DANGEROUS_CALLS = ["eval", "exec", "os.system", "subprocess.call", "subprocess.Popen", "__import__"]

class CodeASTAnalyzer:
    """Safe static AST analyzer inspecting Python code for dangerous function invocations."""
    def analyze_code(self, file_path: str, code_content: str) -> List[SecurityFinding]:
        findings: List[SecurityFinding] = []
        try:
            tree = ast.parse(code_content, filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func_name = ""
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        func_name = f"{getattr(node.func.value, 'id', '')}.{node.func.attr}"

                    if func_name in DANGEROUS_CALLS:
                        findings.append(SecurityFinding(
                            file_path=file_path,
                            line_number=getattr(node, 'lineno', 1),
                            rule_id="SEC-DANGEROUS-CALL",
                            severity=SeverityLevel.HIGH if func_name in ["eval", "exec"] else SeverityLevel.MEDIUM,
                            description=f"Use of dangerous function call '{func_name}' detected.",
                            code_snippet=func_name,
                            recommendation="Avoid arbitrary code execution; use safe parser functions."
                        ))
        except Exception:
            pass
        return findings
