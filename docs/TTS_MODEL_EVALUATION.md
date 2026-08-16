# LALA Local Text-to-Speech (TTS) Model Evaluation

System Identity: **LALA**  
Target User: **Mandar**

---

## 📊 TTS Candidate Evaluation Matrix

| Candidate Engine | Download Size | RAM/VRAM Impact | Languages Supported | Naturalness | Selection Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`Piper TTS` (ONNX)** | ~60 MB / voice | ~50 MB RAM | English, Hindi, Marathi | High (Neural) | **Primary Neural Engine**: Fast local neural TTS, low latency (~50ms), ONNX execution on CPU/GPU. Weights in `F:\LALA\Models\TTS`. |
| **`NativePyttsx3TTS` (SAPI5)** | 0 MB | ~10 MB RAM | English, System Voices | Standard Native | **Fallback Engine**: 100% offline native Windows SAPI5 engine, zero download required, zero-voice-failure guarantee. |
| **`Coqui TTS / IndicTTS`** | ~500 MB | ~1.2 GB VRAM | Hindi, Marathi, English | High | Heavy VRAM footprint; secondary fallback candidate. |

---

## 🎯 Dual-Engine Hybrid Architecture
1. **Primary Neural Engine**: `PiperTTS` stored on `F:\LALA\Models\TTS`.
2. **Fallback Engine**: `NativePyttsx3TTS` (Windows SAPI5) guaranteeing LALA speaks natively even offline or without downloaded voice files.
