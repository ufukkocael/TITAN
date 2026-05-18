# titan-core/titan/tools/docker.py
import asyncio
from typing import Dict, List, Optional

class DockerTool:
    """Docker konteyner yönetimi."""
    
    def __init__(self):
        self.available = self._check_docker()
    
    def _check_docker(self) -> bool:
        """Docker'ın kurulu olup olmadığını kontrol et."""
        import subprocess
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
            return True
        except:
            return False
    
    async def _run(self, *args) -> Dict:
        if not self.available:
            return {"success": False, "error": "Docker kullanılabilir değil."}
        
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker", *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            return {
                "success": proc.returncode == 0,
                "stdout": stdout.decode()[:2000],
                "stderr": stderr.decode()[:500] if stderr else None,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def ps(self) -> Dict:
        return await self._run("ps", "--format", "table {{.Names}}\t{{.Status}}")
    
    async def logs(self, container: str, tail: int = 50) -> Dict:
        return await self._run("logs", "--tail", str(tail), container)
    
    async def restart(self, container: str) -> Dict:
        return await self._run("restart", container)
    
    async def stop(self, container: str) -> Dict:
        return await self._run("stop", container)
    
    async def stats(self, container: Optional[str] = None) -> Dict:
        args = ["stats", "--no-stream"]
        if container:
            args.append(container)
        return await self._run(*args)