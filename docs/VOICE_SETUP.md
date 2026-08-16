# LALA Voice Setup & Troubleshooting Guide

System Identity: **LALA**  
Target User: **Mandar**

---

## 🛠️ Installation & Setup

1. **Verify Dependencies**:
   ```bash
   cd d:\LALA
   py -m pip install -r requirements.txt
   ```

2. **Verify Storage Folders**:
   Ensure `F:\LALA\Models\STT`, `F:\LALA\Models\TTS`, `F:\LALA\Models\WakeWord` exist:
   ```powershell
   New-Item -ItemType Directory -Path "F:\LALA\Models\STT", "F:\LALA\Models\TTS", "F:\LALA\Models\WakeWord" -Force
   ```

3. **Starting Voice Mode**:
   ```bash
   py -m lala.main
   ```
   Inside CLI:
   - Type `/voice` to enter voice mode.
   - Type `/voice-status` to inspect audio devices, VRAM, and latency.
   - Type `/mic` to view and select active microphone.
   - Type `/voice-test` to test local TTS speech output.

---

## 🔒 Privacy Guarantee

- All audio input (microphone) and output (speech synthesis) remain 100% local on `127.0.0.1`.
- `cloud_fallback` remains strictly `false`.
- Voice data is **NEVER** transmitted to cloud APIs.
