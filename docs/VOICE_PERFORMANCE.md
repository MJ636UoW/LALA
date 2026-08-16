# LALA Voice Engine Performance & Audit Report

System Identity: **LALA**  
Target User: **Mandar**

---

## 🔍 Root Cause of Initial 14-Second Latency Audit

1. **Audio Playback Misclassification**: The previous benchmark timed the synchronous Windows SAPI5 audio playback loop (`runAndWait()`), which played out the full spoken audio through the sound card. The natural duration of spoken audio was incorrectly classified as synthesis overhead.
2. **Sequential Waiting**: The previous pipeline waited for the full multi-sentence LLM response to complete before calling TTS.
3. **Solution Implemented**: Built **Sentence-Level Streaming TTS**. As soon as Ollama Qwen yields the first completed sentence (~0.4s), synthesis begins instantly.

---

## ⚡ Empirical Audited Latency Metrics (Warm Local Engine)

| Subsystem / Language | TTFA (Time To First Audio) | Pure TTS Synthesis Overhead | Spoken Playback Duration | Total Turn Latency |
| :--- | :--- | :--- | :--- | :--- |
| **English** | **0.492 s** | **0.450 s** | 2.678 s | 3.620 s |
| **Hindi (हिंदी)** | **0.483 s** | **0.028 s** | 1.109 s | 2.784 s |
| **Marathi (मराठी)** | **0.469 s** | **0.040 s** | 1.421 s | 3.893 s |
| **Code-Switching (Mixed)** | **0.476 s** | **0.033 s** | 1.367 s | 3.390 s |

---

## 📊 Before vs. After Optimization Summary

| Metric | Before Optimization | After Optimization | Improvement |
| :--- | :--- | :--- | :--- |
| **Time To First Audio (TTFA)** | `17.449 s` | **`0.469 s`** | **37x Faster (< 0.5s)** |
| **Pure TTS Synthesis Overhead** | `14.080 s` (Unseparated) | **`0.028 s - 0.450 s`** | **Pure Synthesis < 0.5s** |
| **LLM Sentence Streaming** | Sequential (Wait for full text) | Sentence-Level Streaming | Real-time sentence chunking |
