# services/programmer/agents/coder.py
import os
import subprocess
import re
from typing import Dict, Optional, List
from pathlib import Path

class CoderAgent:
    """Kod yazar, düzeltir, refactor eder."""
    
    def __init__(self, workspace: str = "./workspace"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(exist_ok=True)
    
    def analyze_error(self, error_message: str) -> Dict:
        """Hata mesajından tür ve hedef çıkarır."""
        if any(kw in error_message.lower() for kw in ["memory leak", "not freed", "malloc"]):
            return {"type": "memory_leak", "severity": "high"}
        elif any(kw in error_message.lower() for kw in ["null pointer", "nullptr", "segfault"]):
            return {"type": "null_pointer", "severity": "critical"}
        elif any(kw in error_message.lower() for kw in ["buffer overflow", "heap overflow"]):
            return {"type": "buffer_overflow", "severity": "critical"}
        elif any(kw in error_message.lower() for kw in ["syntax error", "indentation"]):
            return {"type": "syntax_error", "severity": "low"}
        return {"type": "unknown", "severity": "medium"}
    
    def generate_fix(self, error_type: str, file_path: str, line_number: int, context: Dict) -> Optional[str]:
        """Hata türüne göre yama üretir."""
        templates = {
            "memory_leak": 'free({var});  // TITAN auto-fix: memory leak',
            "null_pointer": 'if ({var} == NULL) {{ return {error_code}; }}  // TITAN auto-fix: null check',
            "buffer_overflow": '{var} = realloc({var}, {size} + 1);  // TITAN auto-fix: buffer overflow',
        }
        template = templates.get(error_type)
        if not template:
            return None
        
        return template.format(
            var=context.get("var", "ptr"),
            error_code=context.get("error_code", "-1"),
            size=context.get("size", "1024"),
        )
    
    def apply_patch(self, file_path: str, line_number: int, patch_line: str) -> bool:
        """Yamayı dosyaya uygular, güvenlik kontrolü yapar."""
        # Güvenlik Kontrolü: Sadece izin verilen dizinler
        abs_path = os.path.abspath(file_path)
        if not abs_path.startswith(os.path.abspath(str(self.workspace))):
            print(f"🛑 [SECURITY] Dizin dışı yazma girişimi engellendi: {file_path}")
            return False

        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            if line_number <= len(lines):
                indent = len(lines[line_number - 1]) - len(lines[line_number - 1].lstrip())
                indented = (' ' * max(0, indent)) + patch_line + '\n'
                lines.insert(line_number, indented)
            
            with open(file_path, 'w') as f:
                f.writelines(lines)
            return True
        except Exception:
            return False
    
    def write_code(self, spec: str, language: str = "python") -> Dict:
        """Spesifikasyondan kod üretir (basit template tabanlı)."""
        if language == "python":
            code = f"# TITAN generated: {spec}\n\ndef main():\n    print('{spec}')\n\nif __name__ == '__main__':\n    main()\n"
        else:
            code = f"// TITAN generated: {spec}\n\nfunction main() {{\n    console.log('{spec}');\n}}\nmain();\n"
        
        file_path = self.workspace / f"generated_{hash(spec) % 10000}.{language if language != 'javascript' else 'js'}"
        file_path.write_text(code)
        return {"status": "generated", "file": str(file_path), "language": language}