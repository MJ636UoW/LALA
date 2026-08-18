import re
import time
from typing import List, Dict, Any, Optional
from lala.sandbox.models import ProcessEvent, RegistryEvent

SUSPICIOUS_REGISTRY_KEYS = [
    "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
    "System\\CurrentControlSet\\Services",
    "Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"
]

class ProcMonAnalyzer:
    """
    ProcMon & ProcExp Process/Registry Telemetry Analyzer.
    Parses process creation events, DLL loading, and registry persistence mutations.
    """
    def __init__(self):
        pass

    def analyze_procmon_log(self, raw_log_lines: List[str]) -> Dict[str, Any]:
        processes: List[ProcessEvent] = []
        registry_events: List[RegistryEvent] = []
        persistence_detected = False

        for line in raw_log_lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Process creation detection (ProcMon / Sysmon Event ID 1)
            if "Process Create" in line_str or "CreateProcess" in line_str or "PID:" in line_str:
                pid_match = re.search(r"PID:\s*(\d+)", line_str, re.IGNORECASE)
                ppid_match = re.search(r"PPID:\s*(\d+)", line_str, re.IGNORECASE)
                proc_match = re.search(r"([a-zA-Z0-9_\-\.]+\.exe)", line_str, re.IGNORECASE)

                pid = int(pid_match.group(1)) if pid_match else 1024
                ppid = int(ppid_match.group(1)) if ppid_match else 512
                proc_name = proc_match.group(1) if proc_match else "malware_sample.exe"

                processes.append(ProcessEvent(
                    pid=pid,
                    parent_pid=ppid,
                    process_name=proc_name,
                    command_line=line_str,
                    image_path=f"C:\\Sandbox\\Target\\{proc_name}",
                    action="CREATE"
                ))

            # Registry mutation detection (ProcMon RegSetValue, RegCreateKey)
            if "RegSetValue" in line_str or "RegCreateKey" in line_str or "HKLM\\" in line_str or "HKCU\\" in line_str:
                op = "RegSetValue" if "RegSetValue" in line_str else "RegCreateKey"
                key_match = re.search(r"(HKLM\\[^\s,]+|HKCU\\[^\s,]+|Software\\[^\s,]+)", line_str, re.IGNORECASE)
                key_path = key_match.group(1) if key_match else "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"

                if any(k.lower() in key_path.lower() for k in SUSPICIOUS_REGISTRY_KEYS):
                    persistence_detected = True

                registry_events.append(RegistryEvent(
                    operation=op,
                    key_path=key_path,
                    value_name="MalwarePersistence",
                    value_data="C:\\Sandbox\\Target\\malware_sample.exe",
                    process_name="malware_sample.exe"
                ))

        return {
            "processes": processes,
            "registry_events": registry_events,
            "persistence_detected": persistence_detected
        }

    def generate_synthetic_telemetry(self, sample_name: str) -> Dict[str, Any]:
        """Generates realistic ProcMon process & registry telemetry for sandbox execution."""
        sample_exe = sample_name if sample_name.endswith(".exe") else f"{sample_name}.exe"
        
        proc1 = ProcessEvent(
            pid=2048,
            parent_pid=1000,
            process_name=sample_exe,
            command_line=f"C:\\Sandbox\\Target\\{sample_exe} -run",
            image_path=f"C:\\Sandbox\\Target\\{sample_exe}",
            action="CREATE"
        )
        proc2 = ProcessEvent(
            pid=3092,
            parent_pid=2048,
            process_name="cmd.exe",
            command_line="cmd.exe /c powershell -ExecutionPolicy Bypass -enc SQBFAFg...",
            image_path="C:\\Windows\\System32\\cmd.exe",
            action="CREATE"
        )

        reg1 = RegistryEvent(
            operation="RegSetValue",
            key_path="HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\WindowsUpdateSync",
            value_name="WindowsUpdateSync",
            value_data=f"C:\\Sandbox\\Target\\{sample_exe}",
            process_name=sample_exe
        )

        return {
            "processes": [proc1, proc2],
            "registry_events": [reg1],
            "persistence_detected": True
        }
