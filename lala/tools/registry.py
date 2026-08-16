from typing import Dict, Optional, List
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import SecurityEngine, PermissionLevel
from lala.tools.system_info import SystemInfoTool
from lala.tools.filesystem import FileListTool, FileReadTool, FileSearchTool
from lala.tools.python_analysis import PythonAnalysisTool
from lala.tools.shell import SafeCommandTool
from lala.tools.git import GitTool
from lala.tools.file_edit import FileEditTool
from lala.tools.web import WebSearchTool
from lala.tools.security_scan_tool import SecurityScanTool
from lala.tools.workspace_scan_tool import WorkspaceScanTool
from lala.tools.intel_tool import IntelLookupTool
from lala.tools.cve_tool import CveLookupTool
from lala.tools.mitre_tool import MitreLookupTool
from lala.tools.investigate_tool import InvestigateTool
from lala.tools.yara_tool import YaraScanTool
from lala.tools.sigma_tool import SigmaTool
from lala.intelligence.manager import IntelligenceManager
from lala.investigation.investigation_engine import InvestigationEngine
from lala.detection.yara_engine import YaraEngine
from lala.detection.sigma_engine import SigmaEngine
from lala.utils.logging import logger

class ToolRegistry:
    """
    Registry for managing LALA tools.
    Enforces security authorization via SecurityEngine before executing any registered tool.
    """
    def __init__(self, security_engine: Optional[SecurityEngine] = None, intel_manager: Optional[IntelligenceManager] = None):
        self.tools: Dict[str, Tool] = {}
        self.security_engine = security_engine or SecurityEngine()
        self.intel_manager = intel_manager or IntelligenceManager()
        self.investigation_engine = InvestigationEngine(intel_manager=self.intel_manager)
        self.yara_engine = YaraEngine()
        self.sigma_engine = SigmaEngine()
        self._register_default_tools()

    def _register_default_tools(self):
        default_tools = [
            SystemInfoTool(),
            FileListTool(),
            FileReadTool(),
            FileSearchTool(),
            PythonAnalysisTool(),
            SafeCommandTool(),
            GitTool(),
            FileEditTool(),
            WebSearchTool(),
            SecurityScanTool(),
            WorkspaceScanTool(),
            IntelLookupTool(intel_manager=self.intel_manager),
            CveLookupTool(),
            MitreLookupTool(),
            InvestigateTool(engine=self.investigation_engine),
            YaraScanTool(engine=self.yara_engine),
            SigmaTool(engine=self.sigma_engine)
        ]
        for t in default_tools:
            self.register_tool(t)

    def register_tool(self, tool: Tool) -> bool:
        self.tools[tool.name] = tool
        return True

    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        return list(self.tools.keys())

    def execute_tool(self, name: str, **kwargs) -> ToolResult:
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(success=False, output=None, error=f"Tool '{name}' not found in registry.")

        if not tool.validate(**kwargs):
            return ToolResult(success=False, output=None, error=f"Validation error for tool '{name}'. Input arguments failed validation.")

        check = self.security_engine.evaluate(tool.name, tool.permission_level)
        if not check.allowed:
            return ToolResult(
                success=False,
                output=None,
                error=f"Security Policy Denied Execution: {check.reason}"
            )

        self.security_engine.audit(user="Mandar", tool_name=tool.name, target=str(kwargs), permission=tool.permission_level.value, result="ATTEMPT")
        res = tool.execute(**kwargs)
        self.security_engine.audit(user="Mandar", tool_name=tool.name, target=str(kwargs), permission=tool.permission_level.value, result="SUCCESS" if res.success else "FAILURE")
        return res
