# services/operator/collectors/base.py
import asyncio
import json
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncGenerator, List, Optional

class AsyncBaseCollector(ABC):
    @abstractmethod
    async def stream(self) -> AsyncGenerator[dict, None]:
        pass
    
    @abstractmethod
    def get_command(self) -> List[str]:
        pass
    
    def extract_tags(self, message: str) -> List[str]:
        patterns = [
            r'\b(memory|segfault|null pointer|timeout|OOM|permission denied)\b',
            r'\b(segmentation fault|stack overflow|heap corruption)\b',
            r'\b(openssl|tls|ssl|database|connection)\b',
            r'\b(worker|thread|process|daemon)\b',
        ]
        tags = set()
        for p in patterns:
            tags.update(re.findall(p, message, re.IGNORECASE))
        return list(tags)
    
    def normalize(self, raw: str, source: str) -> Optional[dict]:
        try:
            parsed = json.loads(raw) if raw.startswith('{') else {"message": raw.strip()}
        except json.JSONDecodeError:
            parsed = {"message": raw.strip()}
        if not parsed.get("message"):
            return None
        return {
            "timestamp": parsed.get("timestamp", datetime.utcnow().isoformat()),
            "source": source,
            "platform": source,
            "severity": parsed.get("severity", "INFO"),
            "service": parsed.get("service", "unknown"),
            "message": parsed["message"],
            "tags": self.extract_tags(parsed["message"]),
        }
    
    async def _read(self, stream: asyncio.StreamReader, src: str):
        while True:
            line = await stream.readline()
            if not line: break
            norm = self.normalize(line.decode(errors='replace').strip(), src)
            if norm: yield norm