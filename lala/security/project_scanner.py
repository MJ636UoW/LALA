import os
import re
from pathlib import Path
from typing import List, Optional
from lala.tools.filesystem import is_path_safe
from lala.security.findings import SecurityFinding, SecurityReport, SeverityLevel
from lala.security.code_analyzer import CodeASTAnalyzer

SECRET_PATTERNS = [
    (r'(?i)api[_-]?key\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']', "SEC-SECRET-APIKEY", SeverityLevel.HIGH, "Hardcoded API key pattern detected."),
    (r'(?i)password\s*=\s*["\'][^"\'\s]{6,}["\']', "SEC-SECRET-PASSWORD", SeverityLevel.HIGH, "Hardcoded password assignment detected."),
    (r'(?i)token\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']', "SEC-SECRET-TOKEN", SeverityLevel.HIGH, "Hardcoded token assignment detected.")
]

class CybersecurityProjectScanner:
    """
    Defensive static cybersecurity project scanner for LALA.
    Inspects Python files, config files, and repository assets for dangerous calls and secret leaks.
    Does NOT implement exploit generation or offensive automation.
    """
    def __init__(self, root_path: str = "D:\\LALA"):
        self.root_path = root_path
        self.ast_analyzer = CodeASTAnalyzer()

    def scan_project(self, target_path: Optional[str] = None) -> SecurityReport:
        path_to_scan = target_path or self.root_path
        if not is_path_safe(path_to_scan):
            return SecurityReport()

        canonical = os.path.realpath(path_to_scan)
        target = Path(canonical)
        findings: List[SecurityFinding] = []

        if not target.exists() or not target.is_dir():
            return SecurityReport()

        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["__pycache__", "node_modules", "venv"]]
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), canonical)
                f_lower = f.lower()

                # Check secret file extensions
                if f_lower in [".env", "id_rsa", "id_rsa.pub"] or f_lower.endswith(".pem") or f_lower.endswith(".key"):
                    findings.append(SecurityFinding(
                        file_path=rel_path,
                        line_number=1,
                        rule_id="SEC-SECRET-FILE",
                        severity=SeverityLevel.HIGH,
                        description=f"Potentially sensitive key/credential file '{f}' detected in project tree.",
                        recommendation="Ensure secret files are listed in .gitignore and kept out of Git."
                    ))

                # Static analysis on Python files
                if f_lower.endswith(".py"):
                    full_p = os.path.join(root, f)
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as file_obj:
                            content = file_obj.read(50000)

                        # AST Dangerous Call Check
                        ast_finds = self.ast_analyzer.analyze_code(rel_path, content)
                        findings.extend(ast_finds)

                        # Regex Secret Leak Check
                        for line_no, line in enumerate(content.splitlines(), start=1):
                            for pattern, rule_id, severity, desc in SECRET_PATTERNS:
                                if re.search(pattern, line):
                                    findings.append(SecurityFinding(
                                        file_path=rel_path,
                                        line_number=line_no,
                                        rule_id=rule_id,
                                        severity=severity,
                                        description=desc,
                                        code_snippet=line.strip()[:60],
                                        recommendation="Move sensitive secrets to environment variables."
                                    ))
                    except Exception:
                        pass

        # Calculate counts
        report = SecurityReport(
            total_findings=len(findings),
            critical_count=sum(1 for f in findings if f.severity == SeverityLevel.CRITICAL),
            high_count=sum(1 for f in findings if f.severity == SeverityLevel.HIGH),
            medium_count=sum(1 for f in findings if f.severity == SeverityLevel.MEDIUM),
            low_count=sum(1 for f in findings if f.severity == SeverityLevel.LOW),
            info_count=sum(1 for f in findings if f.severity == SeverityLevel.INFO),
            findings=findings
        )
        return report
