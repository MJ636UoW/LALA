import os
from typing import Dict, Optional

class SecretManager:
    """
    API Key and Secret Manager for LALA Phase 6.
    Loads secrets strictly from environment variables without exposing them to logs, prompts, or Git.
    """
    def __init__(self):
        self._env_keys = {
            "virustotal": "LALA_VIRUSTOTAL_API_KEY",
            "abuseipdb": "LALA_ABUSEIPDB_API_KEY",
            "otx": "LALA_OTX_API_KEY",
            "nvd": "LALA_NVD_API_KEY"
        }

    def get_key(self, provider_name: str) -> Optional[str]:
        p_lower = provider_name.lower()
        env_var = self._env_keys.get(p_lower)
        if not env_var:
            return None
        key = os.environ.get(env_var)
        return key.strip() if key else None

    def has_key(self, provider_name: str) -> bool:
        return self.get_key(provider_name) is not None

    def get_status(self) -> Dict[str, bool]:
        return {provider: self.has_key(provider) for provider in self._env_keys.keys()}
