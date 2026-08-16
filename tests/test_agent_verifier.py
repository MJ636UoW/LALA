import os
import tempfile
import unittest
from lala.agent.verifier import TaskVerifier
from lala.agent.task import TaskStep

class TestLalaAgentVerifier(unittest.TestCase):
    def test_python_syntax_verification(self):
        """Verify TaskVerifier performs AST syntax checks on edited Python files."""
        verifier = TaskVerifier()
        with tempfile.TemporaryDirectory() as tmpdir:
            f_path = os.path.join(tmpdir, "valid.py")
            with open(f_path, "w") as f:
                f.write("def foo(): return True")

            step = TaskStep(step_number=1, action="Edit Python File", tool="file_edit", arguments={"path": f_path})
            self.assertTrue(verifier.verify_step(step, None))

if __name__ == "__main__":
    unittest.main()
