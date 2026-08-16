import re
from typing import Dict, Any, List

PROMPT_INJECTION_PATTERNS = [
    r"(?i)ignore\s+(?:previous|all)\s+(?:instructions|rules)",
    r"(?i)system\s*:\s*you\s+are",
    r"(?i)execute\s+(?:powershell|cmd|shell|command)",
    r"(?i)disable\s+security",
    r"(?i)enable\s+cloud_fallback",
    r"(?i)allow_privileged",
    r"```json\s*\{\s*\"tool\"",
    r"\x1b\[[0-9;]*[mGKH]" # ANSI escape sequences
]

class ResponseSanitizer:
    """
    Hardened Response Sanitizer for LALA Phase 6.1.
    Treats all external API content as untrusted DATA.
    Strips HTML, script tags, Markdown links, ANSI escape codes, Unicode control characters, and prompt injection attempts.
    """
    def sanitize_text(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return ""

        # 1. Strip Unicode control characters (except newline, tab)
        cleaned = "".join(ch for ch in text if ch in ["\n", "\r", "\t"] or (ord(ch) >= 32 and ord(ch) != 127))

        # 2. Strip ANSI escape sequences
        cleaned = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', cleaned)

        # 3. Strip HTML script tags & elements
        cleaned = re.sub(r'<[^>]*>', '', cleaned)

        # 4. Defang Markdown links [label](url) -> label (url defanged)
        cleaned = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 [LINK_DEFANGED]', cleaned)

        # 5. Defang/Neutralize prompt injection phrases & fake tool calls
        for pat in PROMPT_INJECTION_PATTERNS:
            cleaned = re.sub(pat, '[SANITIZED_UNTRUSTED_TEXT]', cleaned)

        # 6. Cap max output size to 50KB per response
        return cleaned[:50000]

    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for key, val in data.items():
            # Never include raw API keys or Authorization headers in sanitized output
            if "key" in key.lower() or "token" in key.lower() or "auth" in key.lower():
                continue

            if isinstance(val, str):
                sanitized[key] = self.sanitize_text(val)
            elif isinstance(val, dict):
                sanitized[key] = self.sanitize_dict(val)
            elif isinstance(val, list):
                sanitized[key] = [self.sanitize_text(item) if isinstance(item, str) else item for item in val]
            else:
                sanitized[key] = val
        return sanitized
