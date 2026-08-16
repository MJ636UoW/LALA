# LALA Voice Hardware Specifications & Diagnostics

System Identity: **LALA**  
Target User: **Mandar**

---

## 📊 Detected System Hardware

- **CPU**: AMD Ryzen 9 5900HX (8 Physical Cores / 16 Logical Processors)
- **RAM**: 16 GB Total System Memory
- **GPU**: **NVIDIA GeForce RTX 3060 Laptop GPU** (6144 MiB VRAM / CUDA 13.2 / Driver 596.36)
- **Disk Free Space**: `F:` (~412 GB Free), `D:` (~105 GB Free), `C:` (~18 GB Free)

---

## 🎙️ Audio Hardware Endpoints

- **Input Device (Microphone)**: `Microphone Array (Realtek(R) Audio)` (Verified native input endpoint)
- **Output Device (Speaker)**: `Speakers (Realtek(R) Audio)` (Verified native audio output endpoint)
- **Host APIs**: Windows DirectSound / WASAPI / MME

---

## 💾 Storage Paths (`D:\LALA` vs `F:\LALA`)

- **Codebase & Scripts**: `D:\LALA`
- **Voice Assets Root**: `F:\LALA\Models\`
  - `F:\LALA\Models\STT`: Speech-to-Text model weights
  - `F:\LALA\Models\TTS`: Text-to-Speech ONNX voice models
  - `F:\LALA\Models\WakeWord`: Local wake word models
