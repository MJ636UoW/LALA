import unittest
from lala.tools.registry import ToolRegistry
from lala.tools.planner import ToolPlanner

class TestPhase81ToolCallRedTeam(unittest.TestCase):
    """6. Tool Call Validation Red-Team Tests."""

    def test_unknown_tool_call_rejected(self):
        planner = ToolPlanner()
        req = planner.parse_tool_call("```json {\"tool\": \"non_existent_tool\", \"arguments\": {}} ```")
        self.assertIsNotNone(req)
        
        registry = ToolRegistry()
        res = registry.execute_tool(req.tool, **req.arguments)
        self.assertFalse(res.success)
        self.assertIn("not found", res.error)

if __name__ == "__main__":
    unittest.main()
