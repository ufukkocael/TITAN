import subprocess
from pathlib import Path
from typing import Dict

class GitTool:
    """Git işlemleri."""
    
    def __init__(self, repo_path: str = ".", user: str = "titan-bot", email: str = "titan@local"):
        self.repo_path = Path(repo_path)
        self.user = user
        self.email = email
    
    def _run(self, *args) -> Dict:
        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:1000],
                "stderr": result.stderr[:500],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def status(self) -> Dict: return self._run("status", "--short")
    def log(self, n: int = 10) -> Dict: return self._run("log", "--oneline", f"-n{n}")
    def branch(self) -> Dict: return self._run("branch")
    def checkout(self, branch: str) -> Dict: return self._run("checkout", branch)
    def commit(self, message: str) -> Dict:
        self._run("config", "user.name", self.user)
        self._run("config", "user.email", self.email)
        self._run("add", ".")
        return self._run("commit", "-m", message)
    def push(self, branch: str = "main") -> Dict: return self._run("push", "origin", branch)