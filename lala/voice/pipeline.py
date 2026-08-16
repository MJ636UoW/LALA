import time
import re
from typing import Optional, Dict, Any, Generator
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
    Features Sentence-Level Streaming TTS for Low Time-To-First-Audio (TTFA < 1.0s).
    """
    def __init__(self, orchestrator: Optional[Orchestrator] = None):
        self.orchestrator = orchestrator or Orchestrator()
        self.device_manager = AudioDeviceManager()
        self.resource_manager = GPUResourceManager()
        
        # Select device for STT
        stt_device = self.resource_manager.select_stt_device("cuda")
        self.stt_engine: SpeechToTextEngine = StubSpeechToText()
        self.tts_engine: BaseTTS = PiperTTS(fallback_engine=NativePyttsx3TTS())
        self.wakeword_engine = WakeWordEngine(wake_word=self.orchestrator.config.system.call_name)
        self.interruption_manager = InterruptionManager(tts_engine=self.tts_engine, wakeword_engine=self.wakeword_engine)
        
        self.last_metrics: Dict[str, float] = {
            "stt_latency": 0.0,
            "llm_first_token_latency": 0.0,
            "tts_ttfa": 0.0,
            "tts_synthesis_overhead": 0.0,
            "audio_playback_duration": 0.0,
            "total_latency": 0.0
        }

    def process_voice_utterance(self, audio_data: bytes, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Processes spoken utterance using sentence-level streaming TTS.
        Measures STT latency, LLM first-token latency, TTFA, synthesis overhead, and playback duration.
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

        # 2. Language Context & LLM Token Streaming
        self.wakeword_engine.set_state(VoiceState.THINKING)
        start_llm = time.time()
        first_token_time: Optional[float] = None
        first_audio_time: Optional[float] = None
        
        system_prompt = self.orchestrator.personality.get_system_prompt(self.orchestrator.state.language_context)
        current_lang = self.orchestrator.state.language_context.primary_language.value
        
        full_response = ""
        sentence_buffer = ""
        total_synthesis_overhead = 0.0
        total_playback_duration = 0.0
        
        self.wakeword_engine.set_state(VoiceState.SPEAKING)

        for token in self.orchestrator.router.route_stream(prompt=transcript, system_prompt=system_prompt):
            if first_token_time is None:
                first_token_time = time.time()
            
            full_response += token
            sentence_buffer += token

            # Detect sentence completion boundaries (. ! ? । \n)
            if re.search(r'[.!?।\n]', sentence_buffer) or len(sentence_buffer.split()) >= 10:
                sentence_to_speak = sentence_buffer.strip()
                if sentence_to_speak:
                    if first_audio_time is None:
                        first_audio_time = time.time()

                    tts_res = self.tts_engine.speak(sentence_to_speak, language=current_lang)
                    total_synthesis_overhead += tts_res.get("synthesis_overhead", 0.0)
                    total_playback_duration += tts_res.get("playback_duration", 0.0)
                
                sentence_buffer = ""

        # Process any remaining trailing sentence buffer
        if sentence_buffer.strip():
            if first_audio_time is None:
                first_audio_time = time.time()
            tts_res = self.tts_engine.speak(sentence_buffer.strip(), language=current_lang)
            total_synthesis_overhead += tts_res.get("synthesis_overhead", 0.0)
            total_playback_duration += tts_res.get("playback_duration", 0.0)

        self.wakeword_engine.set_state(VoiceState.IDLE)
        end_total = time.time()

        llm_first_token = (first_token_time - start_llm) if first_token_time else (end_total - start_llm)
        tts_ttfa = (first_audio_time - start_total) if first_audio_time else (end_total - start_total)

        self.last_metrics = {
            "stt_latency": round(stt_dur, 3),
            "llm_first_token_latency": round(llm_first_token, 3),
            "tts_ttfa": round(tts_ttfa, 3),
            "tts_synthesis_overhead": round(total_synthesis_overhead, 3),
            "audio_playback_duration": round(total_playback_duration, 3),
            "total_latency": round(end_total - start_total, 3)
        }

        # Update orchestrator history
        self.orchestrator.state.add_message("user", transcript, language=self.orchestrator.state.language_context.primary_language)
        self.orchestrator.state.add_message("assistant", full_response, language=self.orchestrator.state.language_context.primary_language)

        return {
            "transcript": transcript,
            "response": full_response,
            "metrics": self.last_metrics
        }
