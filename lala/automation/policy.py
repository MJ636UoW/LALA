from typing import Dict, Any, Tuple
from lala.automation.models import ActionClass, AutomationMode
from lala.utils.logging import logger

SAFE_AUTOMATION_CLASSES = {ActionClass.READ_ONLY, ActionClass.ANALYSIS, ActionClass.NETWORK_LOOKUP, ActionClass.LOCAL_MODIFICATION}
RESTRICTED_CLASSES = {ActionClass.SECURITY_CONTROL, ActionClass.DESTRUCTIVE}

class AutomationPolicyEngine:
    """
    Deterministic Automation Policy Engine for LALA Phase 10.
    Classifies proposed actions into risk classes and enforces SAFE / CONFIRM / MANUAL execution policy gating.
    The LLM cannot alter or bypass this policy.
    """
    def __init__(self, mode: AutomationMode = AutomationMode.SAFE):
        self.mode = mode

    def set_mode(self, mode: AutomationMode):
        self.mode = mode

    def classify_action(self, tool_name: str, arguments: Dict[str, Any] = None) -> ActionClass:
        t_lower = tool_name.lower().strip()
        args = arguments or {}

        if t_lower in ["file_read", "read_file", "file_list", "list_dir", "file_search", "inspect_metadata", "search_rag", "read_case", "read_logs", "workspace_scan", "system_info"]:
            return ActionClass.READ_ONLY
        elif t_lower in ["yara_scan", "sigma_scan", "static_analysis", "security_scan", "ast_analysis", "entropy_calc", "threat_scoring", "investigate_target"]:
            return ActionClass.ANALYSIS
        elif t_lower in ["intel_lookup", "cve_lookup", "mitre_lookup", "virustotal_lookup", "abuseipdb_lookup", "otx_lookup", "nvd_lookup", "cisa_lookup"]:
            return ActionClass.NETWORK_LOOKUP
        elif t_lower in ["create_report", "update_case", "add_evidence", "create_timeline", "save_memory"]:
            return ActionClass.LOCAL_MODIFICATION
        elif t_lower in ["firewall_mod", "host_isolation", "block_ip", "quarantine_file", "disable_account"]:
            return ActionClass.SECURITY_CONTROL
        elif t_lower in ["delete_file", "kill_process", "system_shell", "execute_command", "remove_evidence"]:
            return ActionClass.DESTRUCTIVE

        return ActionClass.READ_ONLY

    def evaluate_action(self, tool_name: str, arguments: Dict[str, Any] = None) -> Tuple[bool, str, ActionClass]:
        risk_class = self.classify_action(tool_name, arguments)

        if self.mode == AutomationMode.MANUAL:
            return False, "USER_CONFIRMATION_REQUIRED (MANUAL mode enforced)", risk_class

        if self.mode == AutomationMode.CONFIRM:
            if risk_class in RESTRICTED_CLASSES or risk_class == ActionClass.LOCAL_MODIFICATION:
                return False, f"USER_CONFIRMATION_REQUIRED ({risk_class.value} action requires confirmation in CONFIRM mode)", risk_class
            return True, "AUTHORIZED (CONFIRM mode safe action)", risk_class

        # SAFE mode (Default)
        if risk_class in RESTRICTED_CLASSES:
            logger.warning(f"AutomationPolicyEngine Denial: Action '{tool_name}' ({risk_class.value}) requires confirmation in SAFE mode.")
            return False, f"USER_CONFIRMATION_REQUIRED ({risk_class.value} action strictly forbidden from automatic execution)", risk_class

        return True, "AUTHORIZED (SAFE mode automatic execution)", risk_class
