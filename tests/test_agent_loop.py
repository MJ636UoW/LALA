import unittest
from lala.tools.planner import ToolPlanner, ToolCallRequest
from lala.tools.executor import ToolExecutor
from lala.tools.registry import ToolRegistry

class TestLalaAgentLoop(unittest.TestCase):
    def test_tool_planner_json_parsing(self):
        """Verify model output JSON parsing by ToolPlanner."""
        planner = ToolPlanner()
        raw_llm_output = 'I will check system info.\n```json\n{"tool": "system_info", "arguments": {}, "reason": "Check specs"}\n```'
        req = planner.parse_tool_call(raw_llm_output)
        self.assertIsNotNone(req)
        self.assertEqual(req.tool, "system_info")

    def test_tool_executor_execution(self):
        """Verify ToolExecutor validates and executes requests through ToolRegistry."""
        registry = ToolRegistry()
        executor = ToolExecutor(registry=registry)
        req = ToolCallRequest(tool="system_info", arguments={})
        res = executor.execute_request(req)
        self.assertTrue(res.success)
        self.assertIn("python_version", res.output)

if __name__ == "__main__":
    unittest.main()
