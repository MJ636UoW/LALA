import unittest
from lala.automation.approvals import ApprovalSystem
from lala.automation.models import ActionClass

class TestAutomationApproval(unittest.TestCase):
    def test_create_and_validate_token(self):
        approvals = ApprovalSystem()
        req = approvals.create_approval_request("case1", "run1", "delete_file", "malware.exe", ActionClass.DESTRUCTIVE, "Testing delete")
        self.assertIsNotNone(req.confirmation_token)

        # Validate token
        valid, msg = approvals.validate_and_consume_token(req.confirmation_token, "case1", "run1", "delete_file", "malware.exe")
        self.assertTrue(valid)

        # Token cannot be reused (single-use check)
        valid_again, msg_again = approvals.validate_and_consume_token(req.confirmation_token, "case1", "run1", "delete_file", "malware.exe")
        self.assertFalse(valid_again)

if __name__ == "__main__":
    unittest.main()
