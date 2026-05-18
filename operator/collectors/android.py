import asyncio
from .base import AsyncBaseCollector
from typing import List

class AndroidCollectorAsync(AsyncBaseCollector):
    def get_command(self) -> List[str]:
        return ["adb", "logcat", "-v", "brief"]
    
    async def stream(self):
        proc = await asyncio.create_subprocess_exec(
            *self.get_command(),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        async for entry in self._read(proc.stdout, "android"):
            yield entry