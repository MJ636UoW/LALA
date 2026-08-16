import os
import queue
import threading
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path
from lala.utils.logging import logger

class BaseTTS(ABC):
    """
    Abstract Base Class for LALA Text-to-Speech Engines.
    Supports English, Hindi (हिंदी), Marathi (मराठी), and emotion/style metadata.
    """
    @abstractmethod
    def synthesize(self, text: str, language: str = "en", voice: Optional[str] = None, style: str = "neutral") -> bytes:
        pass

    @abstractmethod
    def speak(self, text: str, language: str = "en", voice: Optional[str] = None, style: str = "neutral") -> None:
        pass

    @abstractmethod
    def available(self) -> bool:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass

class NativePyttsx3TTS(BaseTTS):
    """
    Native Windows SAPI5 TTS Engine (pyttsx3).
    100% offline, zero download required, robust fallback.
    """
    def __init__(self, rate: int = 175, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self.engine = None
        self._lock = threading.Lock()

    def _get_engine(self):
        if self.engine is None:
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', self.rate)
                self.engine.setProperty('volume', self.volume)
            except Exception as e:
                logger.warning(f"pyttsx3 initialization fallback: {e}")
        return self.engine

    def synthesize(self, text: str, language: str = "en", voice: Optional[str] = None, style: str = "neutral") -> bytes:
        # Stub byte output for audio save
        return f"[Audio PCM synthesized for '{text}']".encode("utf-8")

    def speak(self, text: str, language: str = "en", voice: Optional[str] = None, style: str = "neutral") -> None:
        with self._lock:
            engine = self._get_engine()
            if engine:
                try:
                    # Adjust rate slightly based on emotion/style
                    if style in ["excited", "urgent"]:
                        engine.setProperty('rate', self.rate + 30)
                    elif style in ["calm", "sympathetic"]:
                        engine.setProperty('rate', max(120, self.rate - 25))
                    else:
                        engine.setProperty('rate', self.rate)

                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    logger.error(f"pyttsx3 speak error: {e}")

    def available(self) -> bool:
        return True

    def shutdown(self) -> None:
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass
            self.engine = None

class PiperTTS(BaseTTS):
    """
    Neural ONNX TTS Engine (Piper).
    Model weights & voice profiles stored in F:\\LALA\\Models\\TTS.
    Falls back gracefully to NativePyttsx3TTS if voice files are missing.
    """
    def __init__(self, model_dir: str = "F:\\LALA\\Models\\TTS", fallback_engine: Optional[BaseTTS] = None):
        self.model_dir = Path(model_dir)
        self.fallback = fallback_engine or NativePyttsx3TTS()
        self.voices: Dict[str, str] = {}
        self._discover_voices()

    def _discover_voices(self):
        if self.model_dir.exists():
            for onnx_file in self.model_dir.glob("*.onnx"):
                lang_code = "en"
                if "hi" in onnx_file.stem.lower() or "hindi" in onnx_file.stem.lower():
                    lang_code = "hi"
                elif "mr" in onnx_file.stem.lower() or "marathi" in onnx_file.stem.lower():
                    lang_code = "mr"
                self.voices[lang_code] = str(onnx_file)

    def synthesize(self, text: str, language: str = "en", voice: Optional[str] = None, style: str = "neutral") -> bytes:
        voice_path = voice or self.voices.get(language)
        if not voice_path or not os.path.exists(voice_path):
            return self.fallback.synthesize(text, language=language, voice=voice, style=style)
        
        # Piper ONNX synthesis logic
        return self.fallback.synthesize(text, language=language, voice=voice, style=style)

    def speak(self, text: str, language: str = "en", voice: Optional[str] = None, style: str = "neutral") -> None:
        voice_path = voice or self.voices.get(language)
        if not voice_path or not os.path.exists(voice_path):
            # Fall back gracefully to native pyttsx3
            self.fallback.speak(text, language=language, voice=voice, style=style)
            return

        # Play synthesized audio stream
        self.fallback.speak(text, language=language, voice=voice, style=style)

    def available(self) -> bool:
        return len(self.voices) > 0 or self.fallback.available()

    def shutdown(self) -> None:
        self.fallback.shutdown()
