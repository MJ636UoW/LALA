# LALA Local Brain Specification & Guide

System Identity: **LALA**  
Target User: **Mandar**

---

## 📊 Hardware Findings & Environmental Setup

- **CPU**: AMD Ryzen 9 5900HX (8 Cores, 16 Logical Processors)
- **RAM**: 16 GB System Memory
- **GPU**: **NVIDIA GeForce RTX 3060 Laptop GPU** (6144 MiB VRAM / CUDA 13.2)
- **Disk Free Space**: `F:` (~412 GB Free), `D:` (~105 GB Free), `C:` (~18 GB Free)

---

## 💾 Storage Architecture (`D:\LALA` vs `F:\LALA`)

To prevent filling up drive `C:`, LALA strictly separates source code from large AI model weights and runtime datasets:

- **Source Code Repository**: `D:\LALA` (Git codebase, python modules, configuration, unit tests)
- **Large AI Data Root**: `F:\LALA`
  - `F:\LALA\OllamaModels`: Persistent Ollama model weights (`OLLAMA_MODELS` environment variable)
  - `F:\LALA\Models`: Future custom LLMs & vector embedding models
  - `F:\LALA\Datasets`: Fine-tuning & benchmark datasets
  - `F:\LALA\Memory`: Future persistent vector & RAG databases
  - `F:\LALA\Logs`: Execution diagnostic logs
  - `F:\LALA\Cache`: Model & HTTP response caches
  - `F:\LALA\Backups`: System state backups

---

## 🧠 Selected Model Rationale: `qwen2.5:3b`

### Model Metadata
- **Architecture**: Qwen 2.5 3B Instruct
- **Quantization**: Q4_K_M
- **Download Size**: ~1.9 GB
- **VRAM Footprint**: ~2.2 GB VRAM (Fits **100% inside 6 GB RTX 3060 GPU VRAM**)
- **Inference Speed**: ~50+ tokens/second

### Justification
1. **Multilingual Excellence**: Qwen 2.5 has native Devanagari script tokenization, providing superior fluency in **English**, **Hindi (हिंदी)**, and **Marathi (मराठी)** compared to standard Western LLMs.
2. **Code-Switching Support**: Seamlessly processes mixed-language prompts such as `"माझा Python project check कर आणि explain it in English"`.
3. **VRAM Safety**: Staying around ~2.2 GB VRAM leaves ample ~3.8 GB VRAM headroom for the context window and Windows GPU desktop rendering, preventing out-of-memory crashes.

---

## 🔒 Privacy & Cloud Fallback Policy

- **Local Endpoint**: `http://127.0.0.1:11434`
- **Cloud Fallback**: **DISABLED (`cloud_fallback: false`)**
- **Guarantee**: If Ollama or the local model is offline, LALA reports local brain failure. User prompt data is **NEVER** sent to cloud providers (Gemini/Claude/OpenAI).

---

## 🔍 Diagnostic Commands

Inside the CLI (`py -m lala.main`):
- `/status`: Displays version, runtime health, Ollama endpoint, active model, storage paths, and privacy settings.
- `/model`: Displays active local model information.
- `/lang en|hi|mr`: Switches primary language context.
- `/exit`: Exits the session cleanly.

---

## 🛠️ Model Replacement Procedure

To switch to a different model in the future:
1. Pull the new model via Ollama:
   ```bash
   $env:OLLAMA_MODELS = "F:\LALA\OllamaModels"
   ollama pull <new-model-name>
   ```
2. Update `config/default_config.yaml`:
   ```yaml
   model_router:
     providers:
       local:
         model_name: "<new-model-name>"
   ```
3. Restart LALA CLI (`py -m lala.main`).
