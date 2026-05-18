# api/gateway/middleware/circuit_breaker.py
import time
import asyncio
from enum import Enum
from typing import Dict

class CircuitState(Enum):
    CLOSED = "closed"        # Normal çalışma
    OPEN = "open"            # Devre kesik, istekler reddediliyor
    HALF_OPEN = "half_open"  # Test modu

class CircuitBreaker:
    """Hizmet kesintilerinde devreyi kırarak sistemin geri kalanını korur."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.services: Dict[str, dict] = {}
    
    def _get_service_state(self, service_name: str) -> dict:
        if service_name not in self.services:
            self.services[service_name] = {
                "state": CircuitState.CLOSED,
                "failures": 0,
                "last_failure": 0,
            }
        return self.services[service_name]
    
    async def call(self, service_name: str, func, *args, **kwargs):
        state = self._get_service_state(service_name)
        
        if state["state"] == CircuitState.OPEN:
            if time.time() - state["last_failure"] > self.recovery_timeout:
                state["state"] = CircuitState.HALF_OPEN
            else:
                raise Exception(f"{service_name} şu anda kullanılamıyor (circuit open)")
        
        try:
            result = await func(*args, **kwargs)
            # Başarılı: devreyi kapat
            state["state"] = CircuitState.CLOSED
            state["failures"] = 0
            return result
        except Exception as e:
            state["failures"] += 1
            state["last_failure"] = time.time()
            
            if state["failures"] >= self.failure_threshold:
                state["state"] = CircuitState.OPEN
            
            raise e