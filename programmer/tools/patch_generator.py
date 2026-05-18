# services/programmer/tools/patch_generator.py
import re
from typing import Dict, Optional, List
from pathlib import Path

class PatchGenerator:
    """Gelişmiş yama üreticisi."""
    
    PATCH_TEMPLATES = {
        "memory_leak": {
            "description": "Bellek sızıntısı düzeltmesi",
            "patch": "if ({var}) {{ free({var}); {var} = NULL; }}",
        },
        "null_check": {
            "description": "Null işaretçi kontrolü",
            "patch": "if ({var} == NULL) {{ return {error_code}; }}",
        },
        "buffer_overflow": {
            "description": "Buffer overflow koruması",
            "patch": "{var} = malloc({size} + 1); if ({var}) memset({var}, 0, {size} + 1);",
        },
        "sql_injection": {
            "description": "SQL enjeksiyon koruması",
            "patch": "query = query.replace('\"', '\\\\\"')  // TITAN: input sanitization",
        },
    }
    
    def diagnose(self, error_message: str) -> Optional[str]:
        keywords = {
            "memory_leak": ["memory leak", "not freed", "malloc", "free("],
            "null_pointer": ["null pointer", "nullptr", "segfault", "NoneType"],
            "buffer_overflow": ["buffer overflow", "heap overflow", "stack overflow"],
            "sql_injection": ["sql injection", "unescaped", "sql", "query"],
        }
        for ptype, words in keywords.items():
            if any(w in error_message.lower() for w in words):
                return ptype
        return None
    
    def generate(self, error_type: str, variables: Dict[str, str]) -> Optional[str]:
        template = self.PATCH_TEMPLATES.get(error_type)
        if not template:
            return None
        return f"{template['patch']}  // TITAN auto-fix: {template['description']}"
    
    def create_branch_name(self, fix_type: str) -> str:
        import time
        return f"titan-fix/{fix_type}-{int(time.time()) % 10000}"