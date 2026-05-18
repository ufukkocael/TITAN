# titan-core/titan/tools/terminal.py
import asyncio
import subprocess
from typing import Dict, List

class SafeTerminal:
    """Güvenli terminal erişimi. Tehlikeli komutları engeller."""
    
    BLOCKED_COMMANDS = [
        "rm -rf /", "dd if=", "mkfs.", ":(){ :|:& };:",  # Fork bomb
        "chmod 777 /", "wget", "curl",  # Dış bağlantılar
    ]
    
    ALLOWED_COMMANDS = [
        "ls", "cat", "head", "tail", "wc", "grep", "find",
        "ps", "top", "df", "du", "free", "uptime",
        "git", "python", "pip", "npm", "docker", "systemctl",
    ]
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    def is_safe(self, command: str) -> bool:
        """Bir komutun güvenli olup olmadığını kontrol et."""
        cmd_lower = command.lower().strip()
        
        for blocked in self.BLOCKED_COMMANDS:
            if blocked in cmd_lower:
                return False
        
        base_cmd = cmd_lower.split()[0] if cmd_lower.split() else ""
        return base_cmd in self.ALLOWED_COMMANDS
    
    async def execute(self, command: str) -> Dict:
        """Bir komutu güvenli şekilde çalıştır."""
        if not self.is_safe(command):
            return {
                "success": False,
                "error": "Komut güvenlik politikasını ihlal ediyor.",
                "command": command,
            }
        
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self.timeout
            )
            
            return {
                "success": proc.returncode == 0,
                "stdout": stdout.decode()[:2000],
                "stderr": stderr.decode()[:500] if stderr else None,
                "returncode": proc.returncode,
            }
        except asyncio.TimeoutError:
            return {"success": False, "error": "Komut zaman aşımına uğradı."}
        except Exception as e:
            return {"success": False, "error": str(e)}