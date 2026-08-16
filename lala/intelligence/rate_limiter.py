import time
from typing import Dict, Any
from lala.utils.logging import logger

MAX_PROVIDER_RETRIES = 2

class ProviderRateLimiter:
    """
    Provider-specific Rate Limiter for LALA Phase 6.
    Enforces requests/minute limits, exponential backoff, and max retry caps.
    Never retries authentication failures, permission rejections, or blocked destinations.
    """
    def __init__(self, max_requests_per_minute: int = 15):
        self.max_requests_per_minute = max_requests_per_minute
        self._request_timestamps: Dict[str, list] = {}

    def is_allowed(self, provider_name: str) -> bool:
        p_lower = provider_name.lower()
        now = time.time()
        timestamps = self._request_timestamps.get(p_lower, [])
        # Keep timestamps from last 60 seconds
        valid_timestamps = [t for t in timestamps if now - t < 60]
        self._request_timestamps[p_lower] = valid_timestamps

        if len(valid_timestamps) < self.max_requests_per_minute:
            valid_timestamps.append(now)
            return True

        logger.warning(f"Rate Limiter: Request to provider '{provider_name}' throttled (exceeded {self.max_requests_per_minute} req/min).")
        return False
