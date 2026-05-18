# services/operator/collectors/linux.py
import asyncio
from .base import AsyncBaseCollector
from typing import List

class LinuxCollectorAsync(AsyncBaseCollector):
    def get_command(self) -> List[str]:
        return ["journalctl", "-f", "-o", "json", "-n", "50"]
    
    async def stream(self):
        proc = await asyncio.create_subprocess_exec(
            *self.get_command(),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        async for entry in self._read(proc.stdout, "linux"):
            yield entry