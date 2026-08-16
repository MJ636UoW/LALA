from abc import ABC, abstractmethod
from typing import Optional

class SpeechToTextInterface(ABC):
    """
    Abstract interface for multilingual Speech-To-Text input.
    Model downloads deferred to Phase 4.
    """
    @abstractmethod
    def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> str:
        pass

class TextToSpeechInterface(ABC):
    """
    Abstract interface for multilingual Text-To-Speech output.
    Model downloads deferred to Phase 4.
    """
    @abstractmethod
    def synthesize(self, text: str, language: Optional[str] = None) -> bytes:
        pass

class StubSpeechToText(SpeechToTextInterface):
    """
    Lightweight STT stub for Phase 1 testing.
    """
    def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> str:
        return "[Audio transcription stub for LALA]"

class StubTextToSpeech(TextToSpeechInterface):
    """
    Lightweight TTS stub for Phase 1 testing.
    """
    def synthesize(self, text: str, language: Optional[str] = None) -> bytes:
        return b"[Audio audio synthesis stub for LALA]"
