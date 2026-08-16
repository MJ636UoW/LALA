import re
from typing import Tuple

class YaraValidator:
    """
    Syntax and Security Validator for YARA rules in LALA Phase 7.
    Ensures rules are valid data structures without malicious command sequences.
    """
    def validate_rule_text(self, rule_text: str) -> Tuple[bool, str]:
        if not rule_text or not isinstance(rule_text, str):
            return False, "Empty or invalid rule text."

        # Security Check: Reject shell commands or executable instructions inside comments/meta
        forbidden = ["cmd.exe", "powershell", "format c:", "rmdir /s", "system_shell"]
        for f in forbidden:
            if f in rule_text.lower():
                return False, f"Rule text contains forbidden executable keyword: '{f}'"

        # Syntax Check: Basic YARA structure validation
        if not re.search(r"\brule\s+[A-Za-z0-9_]+\s*\{", rule_text):
            return False, "Syntax Error: Missing 'rule RuleName {' declaration."

        if "condition:" not in rule_text:
            return False, "Syntax Error: Missing 'condition:' section."

        return True, "Valid YARA rule."
