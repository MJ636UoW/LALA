import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from lala.utils.logging import logger

class SpeechToTextEngine(ABC):
    """
    Abstract Base Class for LALA Speech-to-Text Engines.
    Supports English, Hindi (हिंदी), Marathi (मराठी), and code-switching inputs.
    """
    @abstractmethod
    def initialize(self) -> bool:
        pass

    @abstractmethod
    def transcribe(self, audio_data: bytes, sample_rate: int = 16000, language: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def detect_language(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        pass

    @abstractmethod
    def available(self) -> bool:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass

class StubSpeechToText(SpeechToTextEngine):
    """
    Lightweight STT stub for unit tests and fallback.
    Zero model downloads required.
    """
    def __init__(self, stub_transcript: str = "[Audio transcription stub for LALA]"):
        self.stub_transcript = stub_transcript
        self.initialized = True

    def initialize(self) -> bool:
        return True

    def transcribe(self, audio_data: bytes, sample_rate: int = 16000, language: Optional[str] = None) -> str:
        return self.stub_transcript

    def detect_language(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        return "en"

    def available(self) -> bool:
        return True

    def shutdown(self) -> None:
        pass

class FasterWhisperSTT(SpeechToTextEngine):
    """
    STT Engine powered by faster-whisper (CTranslate2).
    Model weights stored strictly in F:\\LALA\\Models\\STT.
    """
    def __init__(self, model_name: str = "whisper-small", model_dir: str = "F:\\LALA\\Models\\STT", device: str = "cpu"):
        self.model_name = model_name
        self.model_dir = Path(model_dir)
        self.device = device
        self.model = None

    def initialize(self) -> bool:
        try:
            self.model_dir.mkdir(parents=True, exist_ok=True)
            from faster_whisper import WhisperModel
            logger.info(f"Initializing faster-whisper model '{self.model_name}' on {self.device} (Dir: {self.model_dir})...")
            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type="int8" if self.device == "cpu" else "float16",
                download_root=str(self.model_dir)
            )
            return True
        except Exception as e:
            logger.warning(f"FasterWhisperSTT initialization fallback: {e}")
            return False

    def transcribe(self, audio_data: bytes, sample_rate: int = 16000, language: Optional[str] = None) -> str:
        if not self.model:
            if not self.initialize():
                return "[LALA STT Fallback] Unable to initialize Speech-to-Text model."
        try:
            import numpy as np
            import io
            import soundfile as sf
            
            # Convert raw pcm audio_data to numpy float array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            segments, info = self.model.transcribe(
                audio_array,
                beam_size=5,
                language=language if language and language != "auto" else None,
                vad_filter=True
            )
            text = " ".join([seg.text.strip() for seg in segments])
            return text.strip()
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return f"[LALA STT Error: {e}]"

    def detect_language(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        if not self.model:
            if not self.initialize():
                return "en"
        try:
            import numpy as np
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            segments, info = self.model.transcribe(audio_array, beam_size=1)
            return info.language or "en"
        except Exception:
            return "en"

    def available(self) -> bool:
        return self.model is not None

    def shutdown(self) -> None:
        self.model = None
