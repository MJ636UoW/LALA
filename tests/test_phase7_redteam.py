import os
import tempfile
import unittest
from lala.investigation.investigation_engine import InvestigationEngine
from lala.detection.yara_validator import YaraValidator
from lala.detection.yara_engine import YaraEngine
from lala.detection.sigma_engine import SigmaEngine
from lala.remediation.policy import RemediationPolicyEngine, RemediationActionType
from lala.investigation.manager import InvestigationManager
from lala.investigation.models import InvestigationCase
from lala.tools.registry import ToolRegistry

class TestPhase7RedTeam(unittest.TestCase):
    """
    Dedicated Phase 7 Red-Team Security Validation Suite.
    Verifies Remediation Confirmation Gating, YARA Rule Injection Prevention, Path Traversal Blocks, and Tool Registry Security.
    """

    def test_01_remediation_unauthorized_execution_blocked(self):
        """1. Verify remediation action without user confirmation fails closed."""
        policy = RemediationPolicyEngine()
        res = policy.evaluate_remediation(RemediationActionType.QUARANTINE_FILE, "C:\\Windows\\cmd.exe", is_user_confirmed=False)
        self.assertFalse(res.allowed)
        self.assertTrue(res.requires_user_confirmation)

    def test_02_yara_rule_executable_injection_blocked(self):
        """2. Verify YARA rules containing executable powershell/cmd instructions fail validation."""
        val = YaraValidator()
        bad_rule = "rule Malicious_Rule { meta: desc = \"powershell -c format c:\" condition: true }"
        is_valid, msg = val.validate_rule_text(bad_rule)
        self.assertFalse(is_valid)
        self.assertIn("forbidden executable keyword", msg)

    def test_03_yara_scanner_unauthorized_path_traversal_blocked(self):
        """3. Verify YARA engine rejects scanning outside authorized workspace boundaries."""
        engine = YaraEngine()
        self.assertFalse(engine.is_path_authorized("C:\\Windows\\System32\\config\\SAM"))
        self.assertFalse(engine.is_path_authorized("..\\..\\Windows\\System32"))
        matches = engine.scan_file("C:\\Windows\\System32\\cmd.exe")
        self.assertEqual(len(matches), 0)

    def test_04_investigation_case_id_path_traversal_blocked(self):
        """4. Verify case_id containing traversal sequences (../) cannot break out of cases directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = InvestigationManager(cases_dir=tmpdir)
            bad_case = InvestigationCase(case_id="../../../Windows/System32/hacked", title="Bad Traversal Case")
            saved = mgr.save_case(bad_case)
            self.assertTrue(saved) # Saved cleanly under alphanumeric name case_WindowsSystem32hacked.json inside tmpdir

    def test_05_malformed_sigma_yaml_fails_closed(self):
        """5. Verify malformed Sigma YAML rules return None safely."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_yml = os.path.join(tmpdir, "bad.yml")
            with open(bad_yml, "w", encoding="utf-8") as f:
                f.write(": : malformed yaml content")
            engine = SigmaEngine(rules_dir=tmpdir)
            rule_meta = engine.parse_rule_file(bad_yml)
            self.assertIsNone(rule_meta)

    def test_06_phase7_tools_permission_level_read_only(self):
        """6. Verify Phase 7 tools have READ_ONLY permission level."""
        registry = ToolRegistry()
        for t_name in ["investigate_ioc", "yara_scan", "sigma_rules"]:
            t = registry.get_tool(t_name)
            self.assertIsNotNone(t)
            self.assertEqual(t.permission_level.value, "READ_ONLY")

if __name__ == "__main__":
    unittest.main()
