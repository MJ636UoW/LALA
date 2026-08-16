import time
from typing import Optional, Dict, Any
from lala.core.orchestrator import Orchestrator
from lala.core.state import LanguageCode
from lala.voice.device import AudioDeviceManager
from lala.voice.stt import SpeechToTextEngine, StubSpeechToText, FasterWhisperSTT
from lala.voice.tts import BaseTTS, NativePyttsx3TTS, PiperTTS
from lala.voice.wakeword import WakeWordEngine, VoiceState
from lala.voice.interruption import InterruptionManager
from lala.voice.resource_manager import GPUResourceManager
from lala.utils.logging import logger

class VoicePipeline:
    """
    End-to-End Multilingual Voice Pipeline for LALA.
    Connects Mic Input -> STT -> Language Context -> Orchestrator -> Ollama -> EmotionState -> TTS -> Speaker Output.
    """
    def __init__(self, orchestrator: Optional[Orchestrator] = None):
        self.orchestrator = orchestrator or Orchestrator()
        self.device_manager = AudioDeviceManager()
        self.resource_manager = GPUResourceManager()
        
        # Select device for STT
        stt_device = self.resource_manager.select_stt_device("cuda")
        self.stt_engine: SpeechToTextEngine = StubSpeechToText()
        self.tts_engine: BaseTTS = NativePyttsx3TTS()
        self.wakeword_engine = WakeWordEngine(wake_word=self.orchestrator.config.system.call_name)
        self.interruption_manager = InterruptionManager(tts_engine=self.tts_engine, wakeword_engine=self.wakeword_engine)
        
        self.last_metrics: Dict[str, float] = {
            "stt_latency": 0.0,
            "llm_first_token_latency": 0.0,
            "tts_latency": 0.0,
            "total_latency": 0.0
        }

    def process_voice_utterance(self, audio_data: bytes, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Process a single spoken utterance through the complete voice pipeline.
        Returns transcript, LLM response, TTS status, and latency metrics.
        """
        start_total = time.time()
        self.wakeword_engine.set_state(VoiceState.LISTENING)

        # 1. Speech-to-Text Transcription
        start_stt = time.time()
        transcript = self.stt_engine.transcribe(audio_data, sample_rate=sample_rate)
        stt_dur = time.time() - start_stt

        if not transcript or transcript.startswith("[LALA STT Error"):
            self.wakeword_engine.set_state(VoiceState.IDLE)
            return {
                "transcript": transcript or "",
                "response": "Could not recognize audio.",
                "metrics": self.last_metrics
            }

        # 2. Language Context & Orchestration
        self.wakeword_engine.set_state(VoiceState.THINKING)
        start_llm = time.time()
        
        # System prompt & prompt routing
        system_prompt = self.orchestrator.personality.get_system_prompt(self.orchestrator.state.language_context)
        llm_response = self.orchestrator.process_user_input(transcript)
        llm_dur = time.time() - start_llm

        # 3. Text-to-Speech Synthesis & Playback
        self.wakeword_engine.set_state(VoiceState.SPEAKING)
        start_tts = time.time()
        
        current_lang = self.orchestrator.state.language_context.primary_language.value
        self.tts_engine.speak(llm_response, language=current_lang, style="neutral")
        tts_dur = time.time() - start_tts

        self.wakeword_engine.set_state(VoiceState.IDLE)
        total_dur = time.time() - start_total

        self.last_metrics = {
            "stt_latency": round(stt_dur, 3),
            "llm_first_token_latency": round(llm_dur, 3),
            "tts_latency": round(tts_dur, 3),
            "total_latency": round(total_dur, 3)
        }

        return {
            "transcript": transcript,
            "response": llm_response,
            "metrics": self.last_metrics
        }
