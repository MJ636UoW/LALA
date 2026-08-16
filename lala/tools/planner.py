import json
import re
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ToolCallRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    reason: str = ""
    risk: str = "READ_ONLY"

class ToolPlanner:
    """
    Parses structured tool requests from LLM model generations.
    Ensures model does not execute tools directly without schema validation and security check.
    """
    def parse_tool_call(self, text: str) -> Optional[ToolCallRequest]:
        # Look for JSON block in output
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        json_str = match.group(1) if match else None

        if not json_str:
            match_raw = re.search(r'(\{\s*"tool"\s*:\s*".*?\}\s*)', text, re.DOTALL)
            json_str = match_raw.group(1) if match_raw else None

        if json_str:
            try:
                data = json.loads(json_str)
                if "tool" in data:
                    return ToolCallRequest(
                        tool=data.get("tool", ""),
                        arguments=data.get("arguments", {}),
                        reason=data.get("reason", ""),
                        risk=data.get("risk", "READ_ONLY")
                    )
            except Exception:
                pass
        return None
