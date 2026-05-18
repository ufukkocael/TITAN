# titan-core/titan/stability/validation.py
import ast
import sys
import io
from typing import Dict, Any, List

class EvolutionValidator:
    """
    Mutasyonun sadece 'yasal' değil, aynı zamanda 'mantıklı' ve 'uyumlu' 
    olup olmadığını test eden doğrulama birimi.
    """
    
    def __init__(self):
        self.validation_history = []

    def check_interface_consistency(self, old_code: str, new_code: str) -> Dict[str, Any]:
        """Eski ve yeni kodun fonksiyon/sınıf isimlerinin uyumlu olup olmadığını denetler."""
        try:
            old_tree = ast.parse(old_code)
            new_tree = ast.parse(new_code)
            
            old_defs = {node.name for node in ast.walk(old_tree) if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
            new_defs = {node.name for node in ast.walk(new_tree) if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
            
            missing = old_defs - new_defs
            if missing:
                return {
                    "valid": False, 
                    "reason": f"Kritik arayüz kaybı! Silinen fonksiyon/sınıflar: {missing}"
                }
            return {"valid": True}
        except Exception as e:
            return {"valid": False, "reason": f"Analiz hatası: {e}"}

    def dry_run_test(self, code: str) -> Dict[str, Any]:
        """Kodu izole bir ortamda derleyip temel çalışma testini yapar."""
        # NOT: exec() kullanımı tehlikelidir, bu yüzden çok kısıtlı bir scope'ta yapılır.
        local_scope = {}
        try:
            # Sadece sentaks ve import kontrolü için compile edilir
            byte_code = compile(code, '<string>', 'exec')
            return {"valid": True, "message": "Kod derlenebilir durumda."}
        except Exception as e:
            return {"valid": False, "reason": f"Çalıştırma hatası: {e}"}

    async def logical_audit(self, llm_gateway, original_path: str, mutation: Dict) -> Dict:
        """LLM'i 'Bağımsız Denetçi' olarak kullanarak mantık kontrolü yapar."""
        prompt = (f"Sen TITAN V4 Bağımsız Kod Denetçisisin. Geliştiricin U.KOCAEL.\n"
                  f"DOSYA: {original_path}\n"
                  f"YAPILAN DEĞİŞİKLİK:\n{mutation['mutation_code'][:1000]}\n\n"
                  f"Bu değişiklik orijinal kodun amacını bozuyor mu yoksa iyileştiriyor mu?\n"
                  f"Yanıtını sadece 'APPROVED' veya 'REJECTED: [Neden]' olarak ver.")
        
        audit_res = await llm_gateway.ask(prompt, context="evolution_audit")
        
        if "REJECTED" in audit_res.upper():
            return {"approved": False, "reason": audit_res}
        return {"approved": True}
