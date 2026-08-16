import threading
from typing import Optional
from lala.voice.tts import BaseTTS
from lala.voice.wakeword import WakeWordEngine, VoiceState
from lala.utils.logging import logger

class InterruptionManager:
    """
    Barge-in / Interruption Manager for LALA.
    Monitors user microphone input during active TTS speech.
    If user speech is detected while LALA is speaking, immediately halts TTS playback and resets audio queue.
    """
    def __init__(self, tts_engine: Optional[BaseTTS] = None, wakeword_engine: Optional[WakeWordEngine] = None):
        self.tts_engine = tts_engine
        self.wakeword_engine = wakeword_engine
        self.is_interrupted = False
        self._lock = threading.Lock()

    def check_and_interrupt(self, energy_level: float, threshold: float = 500.0) -> bool:
        """
        Check incoming audio energy level during TTS playback.
        If energy exceeds threshold while LALA is SPEAKING, trigger barge-in interrupt.
        """
        with self._lock:
            if self.wakeword_engine and self.wakeword_engine.get_state() == VoiceState.SPEAKING:
                if energy_level > threshold:
                    logger.info("Barge-in detected! Halting active LALA speech synthesis...")
                    self.is_interrupted = True
                    if self.tts_engine:
                        self.tts_engine.shutdown()
                    self.wakeword_engine.set_state(VoiceState.LISTENING)
                    return True
        return False

    def reset(self):
        with self._lock:
            self.is_interrupted = False
