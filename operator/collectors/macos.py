import asyncio
from .base import AsyncBaseCollector
from typing import List

class AppleCollectorAsync(AsyncBaseCollector):
    def get_command(self) -> List[str]:
        return ["log", "stream", "--style", "json"]
    
    async def stream(self):
        proc = await asyncio.create_subprocess_exec(
            *self.get_command(),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        async for entry in self._read(proc.stdout, "macos"):
            yield entry