import unittest
from lala.llm.router import LocalModelRouter
from lala.llm.models import TaskType

class TestLLMRouter(unittest.TestCase):
    def test_task_routing_default_model(self):
        router = LocalModelRouter(default_model="qwen2.5:3b")
        self.assertEqual(router.task_model_map[TaskType.CODING], "qwen2.5:3b")

    def test_routing_when_offline_fails_closed(self):
        router = LocalModelRouter(default_model="qwen2.5:3b")
        # When offline, returns LOCAL_MODEL_UNAVAILABLE
        res = router.route_request("Hello", TaskType.GENERAL)
        self.assertIn("LOCAL_MODEL_UNAVAILABLE", res.text)
        self.assertTrue(res.is_local)

if __name__ == "__main__":
    unittest.main()
