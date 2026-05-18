# titan-core/titan/tools/filesystem.py
import os
import shutil
from pathlib import Path
from typing import List, Optional

class SafeFileSystem:
    """Güvenli dosya sistemi erişimi. Sadece izin verilen dizinlerde çalışır."""
    
    def __init__(self, allowed_paths: List[str] = None):
        self.allowed_paths = allowed_paths or ["./workspace", "./data"]
        # Tehlikeli dizinleri engelle
        self.blocked_paths = ["/etc", "/sys", "/proc", "/boot", "C:\\Windows", "C:\\System32"]
    
    def _is_safe(self, path: str) -> bool:
        """Bir yolun güvenli olup olmadığını kontrol et."""
        abs_path = os.path.abspath(path)
        
        for blocked in self.blocked_paths:
            if abs_path.startswith(blocked):
                return False
        
        for allowed in self.allowed_paths:
            if abs_path.startswith(os.path.abspath(allowed)):
                return True
        
        return False
    
    def read(self, path: str) -> Optional[str]:
        """Dosya oku."""
        if not self._is_safe(path):
            return None
        try:
            return Path(path).read_text()
        except Exception:
            return None
    
    def write(self, path: str, content: str) -> bool:
        """Dosya yaz."""
        if not self._is_safe(path):
            return False
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content)
            return True
        except Exception:
            return False
    
    def list_dir(self, path: str) -> List[str]:
        """Dizin içeriğini listele."""
        if not self._is_safe(path):
            return []
        try:
            return os.listdir(path)
        except Exception:
            return []
    
    def delete(self, path: str) -> bool:
        """Dosya sil."""
        if not self._is_safe(path) or not os.path.exists(path):
            return False
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return True
        except Exception:
            return False
    
    def exists(self, path: str) -> bool:
        return self._is_safe(path) and os.path.exists(path)