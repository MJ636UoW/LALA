from typing import Dict, List, Any, Optional
from lala.intelligence.models import AttackTechnique

MITRE_DATABASE: Dict[str, Dict[str, str]] = {
    "T1059": {"name": "Command and Scripting Interpreter", "tactic": "Execution", "desc": "Adversaries may abuse interpreters to execute commands."},
    "T1059.001": {"name": "PowerShell", "tactic": "Execution", "desc": "Adversaries may abuse PowerShell commands."},
    "T1059.003": {"name": "Windows Command Shell", "tactic": "Execution", "desc": "Adversaries may abuse cmd.exe commands."},
    "T1566": {"name": "Phishing", "tactic": "Initial Access", "desc": "Adversaries may send phishing emails with malicious attachments or links."},
    "T1486": {"name": "Data Encrypted for Impact", "tactic": "Impact", "desc": "Adversaries may encrypt data on target systems to interrupt availability."}
}

class MitreAttackEngine:
    """MITRE ATT&CK Mapping & Lookup Helper for LALA."""
    def get_technique(self, technique_id: str) -> Optional[AttackTechnique]:
        tid = technique_id.upper()
        data = MITRE_DATABASE.get(tid)
        if data:
            return AttackTechnique(
                technique_id=tid,
                name=data["name"],
                tactic=data["tactic"],
                description=data["desc"]
            )
        return None

    def search_techniques(self, query: str) -> List[AttackTechnique]:
        q = query.lower()
        matches = []
        for tid, data in MITRE_DATABASE.items():
            if q in tid.lower() or q in data["name"].lower() or q in data["tactic"].lower():
                matches.append(AttackTechnique(
                    technique_id=tid,
                    name=data["name"],
                    tactic=data["tactic"],
                    description=data["desc"]
                ))
        return matches
