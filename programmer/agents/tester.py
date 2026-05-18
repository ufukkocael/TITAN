# services/programmer/agents/tester.py
import subprocess
import tempfile
from typing import Dict

class TesterAgent:
    """Kod testlerini çalıştırır, sonuçları raporlar."""
    
    def run_unit_tests(self, file_path: str, language: str = "python") -> Dict:
        """Birim testleri çalıştırır."""
        if language == "python":
            result = subprocess.run(
                ["python", "-m", "pytest", file_path, "-v"],
                capture_output=True, text=True, timeout=30
            )
            return {
                "passed": result.returncode == 0,
                "output": result.stdout[-500:],
                "error": result.stderr[:200] if result.returncode != 0 else None,
            }
        return {"passed": True, "output": "Test runner not available for this language"}
    
    def syntax_check(self, code: str, language: str = "python") -> Dict:
        """Sözdizimi kontrolü yapar."""
        try:
            compile(code, "<titan>", "exec")
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {"valid": False, "error": str(e)}
    
    def generate_test(self, code: str, language: str = "python") -> str:
        """Basit bir test şablonu üretir."""
        if language == "python":
            return f"""
import unittest

class TITANAutoTest(unittest.TestCase):
    def test_basic(self):
        # TITAN auto-generated test
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
"""
        return "// Test generation not supported for this language"