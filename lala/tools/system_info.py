import sys
import shutil
import os
import subprocess
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel

class SystemInfoTool(Tool):
    """
    Safe automatic tool providing system diagnostics (CPU, RAM, GPU, Storage, Python, Ollama).
    """
    def __init__(self):
        super().__init__(
            name="system_info",
            description="Inspect system hardware specs, CPU, RAM, GPU VRAM, storage, and Ollama status.",
            category="system",
            permission_level=PermissionLevel.SAFE_AUTOMATIC,
            risk_description="Safe automatic system diagnostics read"
        )

    def execute(self, **kwargs) -> ToolResult:
        try:
            ram_total_gb = "N/A"
            ram_avail_gb = "N/A"
            cpu_count = os.cpu_count() or 1

            try:
                import psutil
                mem = psutil.virtual_memory()
                ram_total_gb = round(mem.total / (1024**3), 2)
                ram_avail_gb = round(mem.available / (1024**3), 2)
                cpu_count = psutil.cpu_count(logical=True)
            except ImportError:
                pass

            d_drive = shutil.disk_usage("D:\\") if os.path.exists("D:\\") else None
            f_drive = shutil.disk_usage("F:\\") if os.path.exists("F:\\") else None

            gpu_name = "N/A"
            free_vram_mb = 0
            try:
                res = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name,memory.free", "--format=csv,noheader,nounits"],
                    capture_output=True, text=True, timeout=2
                )
                if res.returncode == 0 and res.stdout.strip():
                    parts = res.stdout.strip().split(",")
                    if len(parts) >= 2:
                        gpu_name = parts[0].strip()
                        free_vram_mb = int(parts[1].strip())
            except Exception:
                pass

            info = {
                "lala_version": "0.4.0 (Phase 4 Agent)",
                "python_version": sys.version.split()[0],
                "cpu_count": cpu_count,
                "ram_total_gb": ram_total_gb,
                "ram_available_gb": ram_avail_gb,
                "gpu_name": gpu_name,
                "free_vram_mb": free_vram_mb,
                "storage": {
                    "D_drive_free_gb": round(d_drive.free / (1024**3), 2) if d_drive else "N/A",
                    "F_drive_free_gb": round(f_drive.free / (1024**3), 2) if f_drive else "N/A"
                }
            }
            return ToolResult(success=True, output=info)
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
