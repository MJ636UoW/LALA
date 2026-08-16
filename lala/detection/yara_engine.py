import os
import hashlib
import re
from pathlib import Path
from typing import List, Optional
from lala.detection.yara_loader import YaraLoader
from lala.detection.yara_models import YaraMatch
from lala.utils.logging import logger

APPROVED_SCAN_WORKSPACE_PATHS = [
    os.path.realpath("D:\\LALA"),
    os.path.realpath("D:\\Projects"),
    os.path.realpath("F:\\LALA")
]

class YaraEngine:
    """
    YARA Rule Scanner Engine for LALA Phase 7.
    Scans authorized local workspace files using validated YARA rules.
    Enforces canonical path containment within D:\\LALA, D:\\Projects, F:\\LALA.
    """
    def __init__(self, rules_dir: str = "F:\\LALA\\Rules\\Yara"):
        self.loader = YaraLoader(rules_dir=rules_dir)

    def is_path_authorized(self, target_path: str) -> bool:
        try:
            canonical = os.path.realpath(target_path)
            for approved in APPROVED_SCAN_WORKSPACE_PATHS:
                if canonical == approved or canonical.startswith(approved + os.sep):
                    return True
        except Exception:
            pass
        return False

    def scan_file(self, target_file_path: str) -> List[YaraMatch]:
        matches: List[YaraMatch] = []
        if not self.is_path_authorized(target_file_path):
            logger.warning(f"YaraEngine Access Denied: Unauthorized scan path '{target_file_path}'")
            return matches

        p = Path(target_file_path)
        if not p.exists() or not p.is_file():
            return matches

        try:
            with open(p, "rb") as f:
                raw_bytes = f.read()
            sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
            content_str = raw_bytes.decode("utf-8", errors="ignore")

            rules = self.loader.load_rules()
            for r in rules:
                rule_name = r["rule_name"]
                rule_content = r["content"]

                # Extract strings to match ($s1 = "val")
                str_patterns = re.findall(r'\$s\d*\s*=\s*"([^"]+)"', rule_content)
                matched_strings = []
                for pat in str_patterns:
                    if pat in content_str:
                        matched_strings.append(pat)

                if matched_strings:
                    matches.append(YaraMatch(
                        rule_name=rule_name,
                        target_path=str(p),
                        sha256=sha256_hash,
                        tags=["yara_match"],
                        matched_strings=matched_strings
                    ))
        except Exception as e:
            logger.error(f"YaraEngine Error scanning '{target_file_path}': {e}")

        return matches

    def scan_directory(self, target_dir_path: str, max_files: int = 100) -> List[YaraMatch]:
        all_matches: List[YaraMatch] = []
        if not self.is_path_authorized(target_dir_path):
            return all_matches

        p = Path(target_dir_path)
        if not p.exists() or not p.is_dir():
            return all_matches

        file_count = 0
        for root, _, files in os.walk(p):
            for file in files:
                if file_count >= max_files:
                    break
                full_path = os.path.join(root, file)
                matches = self.scan_file(full_path)
                all_matches.extend(matches)
                file_count += 1

        return all_matches
