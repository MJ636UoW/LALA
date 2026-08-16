# LALA Local Text-to-Speech (TTS) Model Evaluation & Audit

System Identity: **LALA**  
Target User: **Mandar**

---

## 📊 Active TTS Engine Audit

- **Active Engine**: `NativePyttsx3TTS (Windows SAPI5 Fallback)`
- **Piper Available**: `False` (`F:\LALA\Models\TTS` is currently empty)
- **Sample Rate**: `22050 Hz`
- **Language Support**: English (`en`), Hindi (`hi`), Marathi (`mr`)

---

## 🎯 Piper Voice Model Requirements (Optional Upgrade)

If you wish to download neural `Piper TTS` ONNX models in the future:
1. **English Model**: `en_US-lessac-medium.onnx` (~60 MB) + `en_US-lessac-medium.onnx.json` (~5 KB)
2. **Hindi Model**: `hi_IN-hindi-medium.onnx` (~60 MB) + `hi_IN-hindi-medium.onnx.json` (~5 KB)
3. **Destination Path**: `F:\LALA\Models\TTS`

---

## ⚡ Empirical Audited Synthesis Performance

- **Pure Synthesis Overhead**: `0.028 s - 0.450 s` (28 ms - 450 ms)
- **Time To First Audio (TTFA)**: `0.469 s - 0.492 s` (< 0.5 seconds)
- **Audio Output**: Direct SAPI5 soundcard stream
