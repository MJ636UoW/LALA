import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
from pydantic import BaseModel, Field

def sanitize_storage_path(target_path: str) -> str:
    """Fallback to user home directory if specified drive (e.g. F:\\) does not exist on host system."""
    try:
        drive, _ = os.path.splitdrive(target_path)
        if drive and not os.path.exists(drive + os.sep):
            home_fallback = os.path.expanduser("~/.lala")
            rel = target_path[len(drive):].lstrip("\\/")
            return os.path.join(home_fallback, rel)
    except Exception:
        pass
    return target_path

class SystemConfig(BaseModel):
    name: str = "LALA"
    call_name: str = "LALA"
    voice_identity: str = "LALA"
    personality: str = "LALA"
    user_name: str = "Mandar"
    default_language: str = "en"
    supported_languages: List[str] = Field(default_factory=lambda: ["en", "hi", "mr"])

class StorageConfig(BaseModel):
    root: str = "F:\\LALA"
    models: str = "F:\\LALA\\Models"
    ollama_models: str = "F:\\LALA\\OllamaModels"
    datasets: str = "F:\\LALA\\Datasets"
    memory: str = "F:\\LALA\\Memory"
    logs: str = "F:\\LALA\\Logs"
    cache: str = "F:\\LALA\\Cache"
    backups: str = "F:\\LALA\\Backups"

    @property
    def memory_path(self) -> str:
        base_mem = sanitize_storage_path(self.memory)
        return os.path.join(base_mem, "lala_memory.db")

class SecurityConfig(BaseModel):
    default_permission_level: str = "READ_ONLY"
    allow_privileged_execution: bool = False
    online_intelligence_enabled: bool = False

class ProviderConfig(BaseModel):
    type: str
    model_name: str
    endpoint: str | None = None
    temperature: float = 0.7
    streaming: bool = True

class ModelRouterConfig(BaseModel):
    active_provider: str = "local"
    local_runtime: str = "ollama"
    cloud_fallback: bool = False
    providers: Dict[str, ProviderConfig] = Field(default_factory=dict)

class LalaConfig(BaseModel):
    system: SystemConfig = Field(default_factory=SystemConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    model_router: ModelRouterConfig = Field(default_factory=ModelRouterConfig)

def load_config(config_path: str | Path | None = None) -> LalaConfig:
    if config_path is None:
        base_dir = Path(__file__).resolve().parent.parent.parent
        config_path = base_dir / "config" / "default_config.yaml"
    
    path = Path(config_path)
    if not path.exists():
        return LalaConfig()
    
    with open(path, "r", encoding="utf-8") as f:
        raw_data = yaml.safe_load(f) or {}
    
    return LalaConfig(**raw_data)
