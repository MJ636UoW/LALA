# LALA Voice Engine Performance & Benchmark Report

System Identity: **LALA**  
Target User: **Mandar**

---

## ⏱️ Empirical Latency Measurement

Measured on **AMD Ryzen 9 5900HX**, **NVIDIA RTX 3060 Laptop GPU (6GB VRAM)**, **16GB RAM**:

| Subsystem | Measured Latency | Notes |
| :--- | :--- | :--- |
| **STT Transcription** | `0.000 s` (Stub) / `~0.320 s` (faster-whisper small) | Audio chunk -> Text transcript |
| **LLM Generation** | `3.368 s` | Ollama `qwen2.5:3b` local response |
| **TTS Synthesis & Audio** | `14.080 s` (Full Utterance Playback) | Speech synthesis -> Speaker playback |
| **Total Response Cycle** | `17.449 s` | End-to-end voice turn |

---

## 🚀 Latency Optimization Strategies
1. **Token Streaming to TTS**: Synthesizing audio per completed sentence rather than waiting for the entire LLM response block.
2. **GPU Resource Coordination**: Sequential execution of STT and LLM generation prevents VRAM thrashing on 6GB GPU.
