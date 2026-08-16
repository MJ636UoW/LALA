# LALA Voice Setup & Performance Guide

System Identity: **LALA**  
Target User: **Mandar**

---

## ⚡ Performance Audit & Latency Guarantee

- **Time To First Audio (TTFA)**: **`< 0.5 seconds`** (Empirical audit: `0.469s - 0.492s`)
- **Pure TTS Synthesis Overhead**: **`28ms - 450ms`**
- **Sentence-Level Streaming**: Sentence-by-sentence TTS synthesis as Ollama streams tokens.

---

## 🛠️ CLI Voice Commands

```bash
cd d:\LALA
py -m lala.main
```

Commands:
- `/voice`        : Enters voice conversation mode.
- `/voice-status` : Displays microphone, speaker, STT, TTS, VRAM, and latency metrics.
- `/mic`          : Lists available audio input devices (e.g. `/mic 0`).
- `/voice-test`   : Tests local speech synthesis output.
- `/voice-stop`   : Returns to text mode.

---

## 🔒 Privacy Guarantee

- 100% local voice processing (`cloud_fallback: false`).
- Zero cloud audio APIs.
