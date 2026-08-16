import unittest
from lala.agent.recovery import TaskRecoveryManager, MAX_RETRIES
from lala.agent.task import TaskStep, TaskRisk

class TestLalaAgentRecovery(unittest.TestCase):
    def test_safe_retry_limit(self):
        """Verify TaskRecoveryManager allows up to MAX_RETRIES for safe errors."""
        rec = TaskRecoveryManager()
        step = TaskStep(step_number=1, action="Read File", tool="file_read", risk=TaskRisk.READ_ONLY)
        
        self.assertTrue(rec.should_retry(step, "Temporary I/O Error"))
        self.assertTrue(rec.should_retry(step, "Temporary I/O Error"))
        self.assertFalse(rec.should_retry(step, "Temporary I/O Error")) # Exceeds MAX_RETRIES

    def test_refuse_security_denial_retry(self):
        """Verify TaskRecoveryManager refuses retrying permission denials."""
        rec = TaskRecoveryManager()
        step = TaskStep(step_number=1, action="Privileged Command", tool="system_shell", risk=TaskRisk.PRIVILEGED)
        self.assertFalse(rec.should_retry(step, "Security Policy Denied Execution"))

if __name__ == "__main__":
    unittest.main()
