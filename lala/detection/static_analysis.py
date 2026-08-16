import os
import ast
import math
import hashlib
from pathlib import Path
from typing import Dict, List, Any
from pydantic import BaseModel, Field
from lala.detection.yara_engine import YaraEngine

class StaticAnalysisResult(BaseModel):
    file_path: str
    file_name: str
    file_size_bytes: int
    sha256: str
    sha1: str
    md5: str
    entropy: float
    suspicious_strings: List[str] = Field(default_factory=list)
    ast_suspicious_nodes: List[str] = Field(default_factory=list)
    yara_matches: List[str] = Field(default_factory=list)

class LocalStaticAnalyzer:
    """
    Local Malware & File Static Analysis Engine for LALA Phase 7.
    Performs non-execution analysis of files (hashes, entropy, strings, AST security checks, YARA matches).
    Enforces canonical path authorization within D:\\LALA, D:\\Projects, F:\\LALA.
    """
    def __init__(self):
        self.yara_engine = YaraEngine()

    def calculate_entropy(self, data: bytes) -> float:
        if not data:
            return 0.0
        entropy = 0.0
        length = len(data)
        occ = {}
        for b in data:
            occ[b] = occ.get(b, 0) + 1
        for count in occ.values():
            p = count / length
            entropy -= p * math.log2(p)
        return round(entropy, 3)

    def analyze_python_ast(self, content_str: str) -> List[str]:
        suspicious_nodes = []
        try:
            tree = ast.parse(content_str)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ["eval", "exec", "__import__"]:
                            suspicious_nodes.append(f"Dangerous call: {node.func.id}()")
                    elif isinstance(node.func, ast.Attribute):
                        if node.func.attr in ["system", "Popen", "spawn", "rmtree"]:
                            suspicious_nodes.append(f"Dangerous call: .{node.func.attr}()")
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ["subprocess", "socket", "ctypes", "winreg"]:
                            suspicious_nodes.append(f"Suspicious import: {alias.name}")
        except Exception:
            pass
        return suspicious_nodes

    def analyze_file(self, target_path: str) -> StaticAnalysisResult:
        if not self.yara_engine.is_path_authorized(target_path):
            raise PermissionError(f"Access Denied: Path '{target_path}' outside authorized workspace boundaries.")

        p = Path(target_path)
        if not p.exists() or not p.is_file():
            raise FileNotFoundError(f"File not found: '{target_path}'")

        with open(p, "rb") as f:
            data = f.read()

        sha256 = hashlib.sha256(data).hexdigest()
        sha1 = hashlib.sha1(data).hexdigest()
        md5 = hashlib.md5(data).hexdigest()
        entropy = self.calculate_entropy(data)

        content_str = data.decode("utf-8", errors="ignore")
        
        # Suspicious strings search
        suspicious = []
        keywords = ["powershell", "cmd.exe", "base64_decode", "eval(", "subprocess", "socket", "Keylogger", "WannaCry"]
        for kw in keywords:
            if kw.lower() in content_str.lower():
                suspicious.append(kw)

        # Python AST Analysis if python file
        ast_findings = []
        if p.suffix == ".py":
            ast_findings = self.analyze_python_ast(content_str)

        # YARA scanning
        yara_matches_objs = self.yara_engine.scan_file(str(p))
        yara_rule_names = [m.rule_name for m in yara_matches_objs]

        return StaticAnalysisResult(
            file_path=str(p),
            file_name=p.name,
            file_size_bytes=len(data),
            sha256=sha256,
            sha1=sha1,
            md5=md5,
            entropy=entropy,
            suspicious_strings=suspicious,
            ast_suspicious_nodes=ast_findings,
            yara_matches=yara_rule_names
        )
