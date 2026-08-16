# LALA Local Speech-to-Text (STT) Model Evaluation

System Identity: **LALA**  
Target User: **Mandar**

---

## 📊 STT Candidate Evaluation Matrix

| Candidate Model | Approx Size | VRAM Impact | Languages Supported | Windows CUDA | Selection Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`faster-whisper-small`** | ~460 MB | ~400 MB VRAM | English, Hindi, Marathi, Code-Switching | ✅ Supported | **Primary Selected**: Optimal balance of Devanagari accuracy, low VRAM footprint (~400MB), and fast CTranslate2 C++ inference. |
| **`faster-whisper-base`** | ~140 MB | ~200 MB VRAM | English, Hindi, Marathi | ✅ Supported | **Fast Fallback**: Ultra-lightweight for constrained RAM/VRAM environments. |
| **`openai-whisper-medium`** | ~1.5 GB | ~1.8 GB VRAM | English, Hindi, Marathi | ✅ Supported | High accuracy but higher VRAM overhead alongside Ollama LLM. |
| **`StubSpeechToText`** | 0 MB | 0 MB | English, Hindi, Marathi | ✅ Supported | **Offline Unit Test Stub**: Instant zero-dependency testing. |

---

## 🎯 Final Selected Primary STT Model
- **Engine**: `faster-whisper` (CTranslate2 backend)
- **Model**: `whisper-small` (or `whisper-base`)
- **Storage Location**: `F:\LALA\Models\STT`
- **Execution Mode**: CUDA GPU (auto-fallback to CPU if VRAM < 800 MB free)
