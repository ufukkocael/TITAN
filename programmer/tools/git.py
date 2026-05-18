# services/programmer/tools/git.py
import subprocess
import os
from typing import Dict, Optional
from pathlib import Path

class GitTool:
    """Git işlemleri için araç."""
    
    def __init__(self, repo_path: str, user: str = "titan-bot", email: str = "titan@company.com"):
        self.repo_path = Path(repo_path)
        self.user = user
        self.email = email
    
    def _run(self, *args) -> Dict:
        result = subprocess.run(
            ["git"] + list(args),
            cwd=self.repo_path,
            capture_output=True, text=True
        )
        return {"success": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}
    
    def create_branch(self, branch_name: str) -> Dict:
        return self._run("checkout", "-b", branch_name)
    
    def commit(self, message: str) -> Dict:
        self._run("config", "user.name", self.user)
        self._run("config", "user.email", self.email)
        self._run("add", ".")
        return self._run("commit", "-m", message)
    
    def push(self, branch: str) -> Dict:
        return self._run("push", "origin", branch)
    
    def create_pr(self, title: str, body: str) -> Dict:
        return self._run("pr", "create", "--title", title, "--body", body)
    
    def status(self) -> Dict:
        return self._run("status", "--short")