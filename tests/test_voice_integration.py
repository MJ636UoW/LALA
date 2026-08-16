import unittest
from lala.voice.pipeline import VoicePipeline
from lala.voice.device import AudioDeviceManager

class TestLalaVoiceIntegration(unittest.TestCase):
    """
    Live integration test suite testing voice device discovery and audio pipeline.
    Non-blocking: skips gracefully if hardware or models are unavailable.
    """
    @classmethod
    def setUpClass(cls):
        cls.manager = AudioDeviceManager()
        mics = cls.manager.list_input_devices()
        if not mics:
            raise unittest.SkipTest("No audio input devices found on system.")

    def test_pipeline_execution(self):
        """Test voice pipeline end-to-end processing with audio input."""
        pipeline = VoicePipeline()
        dummy_pcm = b"\x00\x00" * 16000
        result = pipeline.process_voice_utterance(dummy_pcm)
        self.assertIsNotNone(result)
        self.assertIn("metrics", result)
        self.assertIn("stt_latency", result["metrics"])

if __name__ == "__main__":
    unittest.main()
