import time
import math
from typing import List, Optional
from pydantic import BaseModel

class ClapDetectionResult(BaseModel):
    detected: bool
    confidence: float
    timestamp: float

class ClapDetector:
    """
    Hands-Free Clap & Transient Sound Detector for LALA.
    Detects sudden high-amplitude audio spikes characteristic of a hand clap.
    """
    def __init__(self, amplitude_threshold: float = 0.65, min_interval_sec: float = 0.5):
        self.amplitude_threshold = amplitude_threshold
        self.min_interval_sec = min_interval_sec
        self.last_clap_time = 0.0

    def process_pcm_chunk(self, audio_data: bytes) -> ClapDetectionResult:
        now = time.time()
        if now - self.last_clap_time < self.min_interval_sec:
            return ClapDetectionResult(detected=False, confidence=0.0, timestamp=now)

        if not audio_data or len(audio_data) < 4:
            return ClapDetectionResult(detected=False, confidence=0.0, timestamp=now)

        # Convert 16-bit PCM bytes to peak amplitude
        max_val = 0
        for i in range(0, len(audio_data) - 1, 2):
            sample = int.from_bytes(audio_data[i:i+2], byteorder="little", signed=True)
            if abs(sample) > max_val:
                max_val = abs(sample)

        norm_amplitude = max_val / 32768.0
        if norm_amplitude >= self.amplitude_threshold:
            self.last_clap_time = now
            confidence = min(1.0, norm_amplitude)
            return ClapDetectionResult(detected=True, confidence=confidence, timestamp=now)

        return ClapDetectionResult(detected=False, confidence=0.0, timestamp=now)
