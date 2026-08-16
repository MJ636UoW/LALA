import unittest
from lala.automation.workflow import AutonomousWorkflowEngine

class TestAutomationPauseResume(unittest.TestCase):
    def test_pause_and_resume(self):
        engine = AutonomousWorkflowEngine()
        self.assertFalse(engine.is_paused)
        engine.pause()
        self.assertTrue(engine.is_paused)
        engine.resume()
        self.assertFalse(engine.is_paused)

if __name__ == "__main__":
    unittest.main()
