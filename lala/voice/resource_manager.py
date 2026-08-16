from typing import Dict, Any, Optional
from lala.utils.logging import logger

class GPUResourceManager:
    """
    Coordinates GPU and VRAM resources for STT, LLM (Ollama qwen2.5:3b), and TTS processing.
    Ensures safe execution on 6 GB RTX 3060 VRAM, avoiding OOM memory fragmentation.
    """
    def __init__(self, max_vram_mb: int = 5800):
        self.max_vram_mb = max_vram_mb
        self.active_stt_engine: Optional[str] = None
        self.active_tts_engine: Optional[str] = None

    def get_gpu_status(self) -> Dict[str, Any]:
        status = {
            "cuda_available": False,
            "gpu_name": "N/A",
            "total_vram_mb": 0,
            "free_vram_mb": 0,
            "recommended_device": "cpu"
        }
        try:
            import subprocess
            res = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=3
            )
            if res.returncode == 0 and res.stdout.strip():
                parts = [p.strip() for p in res.stdout.strip().split(",")]
                if len(parts) >= 3:
                    gpu_name = parts[0]
                    total_mb = int(parts[1])
                    free_mb = int(parts[2])
                    status.update({
                        "cuda_available": True,
                        "gpu_name": gpu_name,
                        "total_vram_mb": total_mb,
                        "free_vram_mb": free_mb,
                        "recommended_device": "cuda" if free_mb > 1000 else "cpu"
                    })
        except Exception as e:
            logger.debug(f"NVIDIA SMI status query check: {e}")
        return status

    def select_stt_device(self, preferred: str = "cuda") -> str:
        status = self.get_gpu_status()
        if preferred == "cuda" and status.get("cuda_available") and status.get("free_vram_mb", 0) > 800:
            return "cuda"
        return "cpu"
