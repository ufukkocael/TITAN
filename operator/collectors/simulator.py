# services/operator/collectors/simulator.py
import asyncio
import random
from datetime import datetime
from .base import AsyncBaseCollector
from typing import List, AsyncGenerator

class SimulatedCollector(AsyncBaseCollector):
    """Gerçek log kaynağı olmayan test ortamları için sahte log üretir."""
    
    def __init__(self, platform: str = "linux", crash_after: int = 30):
        self.platform = platform
        self.crash_after = crash_after
        self.counter = 0
    
    def get_command(self) -> List[str]:
        return ["echo", "simulated"]
    
    async def stream(self) -> AsyncGenerator[dict, None]:
        normal = [
            "INFO: Connection pool healthy",
            "DEBUG: Cache hit ratio 0.95",
            "INFO: Request completed in 12ms",
            "WARN: Disk usage at 78%",
        ]
        crash = [
            "FATAL: OpenSSL 3.2 heap corruption at 0x7f8a...",
            "CRITICAL: OOM killer invoked for worker_12",
            "FATAL: Segmentation fault in libssl.so.3.2",
            "ERROR: memory leak detected in module auth",
        ]
        attacks = [
            "WARN: Brute force attack detected from 192.168.1.105 (failed logins: 15)",
            "WARN: SQL Injection attempt in URL: /api/users?id=1' OR '1'='1",
            "WARN: Port scan detected from 10.0.0.45",
        ]
        
        while True:
            self.counter += 1
            crash_mode = self.counter > self.crash_after
            attack_mode = self.counter % 15 == 0 # Her 15 logda bir saldırı simüle et
            
            if attack_mode:
                msg = random.choice(attacks)
            else:
                msg = random.choice(crash if crash_mode else normal)
            
            sev = "FATAL" if "FATAL" in msg else ("CRITICAL" if "CRITICAL" in msg else ("ERROR" if "ERROR" in msg else ("WARN" if "WARN" in msg else "INFO")))
            
            ip_match = __import__('re').search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', msg)
            ip = ip_match.group(1) if ip_match else None

            yield {
                "timestamp": datetime.utcnow().isoformat(),
                "source": self.platform,
                "platform": self.platform,
                "severity": sev,
                "service": "security_monitor" if attack_mode else ("openssl_worker" if crash_mode else "app_server"),
                "message": msg,
                "tags": ["attack", "firewall"] if attack_mode else (["openssl", "memory"] if crash_mode else []),
                "ip": ip
            }
            await asyncio.sleep(0.3)