import unittest
from lala.voice.device import AudioDeviceManager
from lala.voice.stt import StubSpeechToText
from lala.voice.tts import NativePyttsx3TTS
from lala.voice.wakeword import WakeWordEngine, VoiceState
from lala.voice.interruption import InterruptionManager
from lala.voice.resource_manager import GPUResourceManager

class TestLalaVoiceUnit(unittest.TestCase):
    def test_audio_device_manager(self):
        """Verify device enumeration and mic selection abstraction."""
        manager = AudioDeviceManager()
        inputs = manager.list_input_devices()
        outputs = manager.list_output_devices()
        self.assertGreater(len(inputs), 0)
        self.assertGreater(len(outputs), 0)

        # Test selecting device
        first_id = inputs[0]["id"]
        res = manager.set_input_device(first_id)
        self.assertTrue(res)

    def test_stt_stub(self):
        """Verify offline STT stub functions without model downloads."""
        stt = StubSpeechToText()
        self.assertTrue(stt.available())
        res = stt.transcribe(b"dummy_pcm")
        self.assertIn("LALA", res)
        lang = stt.detect_language(b"dummy_pcm")
        self.assertEqual(lang, "en")

    def test_tts_native(self):
        """Verify native TTS fallback interface."""
        tts = NativePyttsx3TTS()
        self.assertTrue(tts.available())
        synth = tts.synthesize("Hello Mandar")
        self.assertIsNotNone(synth)

    def test_wakeword_state_machine(self):
        """Verify voice state machine transitions."""
        engine = WakeWordEngine(wake_word="LALA")
        self.assertEqual(engine.get_state(), VoiceState.IDLE)
        
        engine.set_state(VoiceState.LISTENING)
        self.assertEqual(engine.get_state(), VoiceState.LISTENING)
        
        engine.set_state(VoiceState.THINKING)
        self.assertEqual(engine.get_state(), VoiceState.THINKING)
        
        engine.set_state(VoiceState.SPEAKING)
        self.assertEqual(engine.get_state(), VoiceState.SPEAKING)

    def test_interruption_manager(self):
        """Verify barge-in interruption logic."""
        tts = NativePyttsx3TTS()
        engine = WakeWordEngine(wake_word="LALA")
        manager = InterruptionManager(tts_engine=tts, wakeword_engine=engine)
        
        engine.set_state(VoiceState.SPEAKING)
        interrupted = manager.check_and_interrupt(energy_level=800.0, threshold=500.0)
        self.assertTrue(interrupted)
        self.assertEqual(engine.get_state(), VoiceState.LISTENING)

    def test_gpu_resource_manager(self):
        """Verify GPU status check abstraction."""
        gpu_mgr = GPUResourceManager()
        status = gpu_mgr.get_gpu_status()
        self.assertIn("cuda_available", status)
        device = gpu_mgr.select_stt_device("cuda")
        self.assertIn(device, ["cuda", "cpu"])

if __name__ == "__main__":
    unittest.main()
