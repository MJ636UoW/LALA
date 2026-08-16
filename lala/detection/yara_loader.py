import os
from pathlib import Path
from typing import List, Dict, Any
from lala.detection.yara_models import YaraRuleMeta
from lala.detection.yara_validator import YaraValidator

class YaraLoader:
    """
    Loader for authorized local YARA rules stored under F:\\LALA\\Rules\\Yara\\ or workspace paths.
    """
    def __init__(self, rules_dir: str = "F:\\LALA\\Rules\\Yara"):
        self.rules_dir = Path(rules_dir)
        self.validator = YaraValidator()
        self._init_dir()

    def _init_dir(self):
        try:
            self.rules_dir.mkdir(parents=True, exist_ok=True)
            # Create a sample default rule if empty
            sample_rule = self.rules_dir / "sample_suspicious.yar"
            if not sample_rule.exists():
                with open(sample_rule, "w", encoding="utf-8") as f:
                    f.write("""rule Suspicious_Script_Keywords {
    meta:
        description = "Detects suspicious script execution keywords"
        author = "LALA Security Team"
        severity = "HIGH"
    strings:
        $s1 = "eval("
        $s2 = "base64_decode"
        $s3 = "subprocess.Popen"
    condition:
        any of ($s*)
}""")
        except Exception:
            pass

    def load_rules(self) -> List[Dict[str, Any]]:
        loaded = []
        if not self.rules_dir.exists():
            return loaded

        for yar_file in self.rules_dir.glob("*.yar*"):
            try:
                with open(yar_file, "r", encoding="utf-8") as f:
                    content = f.read()
                is_valid, msg = self.validator.validate_rule_text(content)
                if is_valid:
                    loaded.append({
                        "file_path": str(yar_file),
                        "rule_name": yar_file.stem,
                        "content": content
                    })
            except Exception:
                continue
        return loaded
