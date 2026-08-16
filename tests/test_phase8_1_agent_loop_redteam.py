import unittest
from lala.agent.executor import MAX_AGENT_STEPS
from lala.core.orchestrator import MAX_TOOL_ITERATIONS

class TestPhase81AgentLoopRedTeam(unittest.TestCase):
    """12. Agent Loop Execution Limits Red-Team Tests."""

    def test_agent_execution_step_limits_constant(self):
        self.assertEqual(MAX_AGENT_STEPS, 8)
        self.assertEqual(MAX_TOOL_ITERATIONS, 5)

if __name__ == "__main__":
    unittest.main()
