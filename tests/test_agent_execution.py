import unittest
from lala.agent.executor import AgentExecutor, MAX_AGENT_STEPS
from lala.agent.planner import TaskPlanner

class TestLalaAgentExecution(unittest.TestCase):
    def test_agent_execution_plan(self):
        """Verify AgentExecutor executes plans bounded by MAX_AGENT_STEPS."""
        planner = TaskPlanner()
        plan = planner.create_plan_for_goal("Analyze Python project security")
        executor = AgentExecutor()
        result = executor.execute_plan(plan)
        self.assertTrue(result.success)
        self.assertLessEqual(result.steps_executed, MAX_AGENT_STEPS)

if __name__ == "__main__":
    unittest.main()
