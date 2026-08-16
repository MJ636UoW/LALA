from enum import Enum
from typing import Optional, Callable
from lala.utils.logging import logger

class VoiceState(str, Enum):
    IDLE = "IDLE"
    WAKE_WORD_DETECTED = "WAKE_WORD_DETECTED"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"

class WakeWordEngine:
    """
    Wake-word engine and voice state machine manager.
    Coordinates transition states (IDLE -> WAKE_WORD_DETECTED -> LISTENING -> THINKING -> SPEAKING -> IDLE).
    Model storage path: F:\\LALA\\Models\\WakeWord.
    """
    def __init__(self, wake_word: str = "LALA", model_path: str = "F:\\LALA\\Models\\WakeWord"):
        self.wake_word = wake_word
        self.model_path = model_path
        self._state = VoiceState.IDLE
        self._on_state_change: Optional[Callable[[VoiceState], None]] = None

    def get_state(self) -> VoiceState:
        return self._state

    def set_state(self, state: VoiceState):
        if self._state != state:
            logger.info(f"Voice State Transition: {self._state.value} -> {state.value}")
            self._state = state
            if self._on_state_change:
                self._on_state_change(state)

    def register_state_change_callback(self, callback: Callable[[VoiceState], None]):
        self._on_state_change = callback

    def detect_wake_word(self, audio_chunk: bytes) -> bool:
        # Stub wake-word detection for Phase 3 state machine contract
        return False
