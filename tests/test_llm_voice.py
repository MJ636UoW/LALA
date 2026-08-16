import unittest
from lala.core.orchestrator import Orchestrator
from lala.voice.pipeline import VoicePipeline

class TestLLMVoice(unittest.TestCase):
    def test_voice_uses_orchestrator_local_llm(self):
        orch = Orchestrator()
        pipeline = VoicePipeline(orchestrator=orch)
        self.assertEqual(pipeline.orchestrator.local_llm_manager.get_current_model(), "qwen2.5:3b")

if __name__ == "__main__":
    unittest.main()
