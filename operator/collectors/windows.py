import asyncio
import subprocess
from .base import AsyncBaseCollector
from typing import List

class WindowsCollectorAsync(AsyncBaseCollector):
    def get_command(self) -> List[str]:
        return [
            "powershell.exe",
            "-Command",
            "Get-WinEvent -FilterHashtable @{LogName='System'} -MaxEvents 100 | "
            "ForEach-Object { $_.ToXml() }"
        ]
    
    async def stream(self):
        try:
            proc = await asyncio.create_subprocess_exec(
                *self.get_command(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            async for entry in self._read(proc.stdout, "windows"):
                yield entry
            return
        except NotImplementedError:
            pass

        proc = subprocess.Popen(
            self.get_command(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )

        while True:
            line_bytes = await asyncio.to_thread(proc.stdout.readline)
            if not line_bytes:
                break
            line = line_bytes.decode("utf-8", errors="replace")
            norm = self.normalize(line.strip(), "windows")
            if norm:
                yield norm

        proc.stdout.close()
        proc.stderr.close()
        proc.wait()
