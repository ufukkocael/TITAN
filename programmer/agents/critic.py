# services/programmer/agents/critic.py
from typing import Dict

class CriticAgent:
    """Kod kalitesini değerlendirir, güvenlik ve stil kontrolü yapar."""
    
    def review(self, code: str, context: Dict = {}) -> Dict:
        issues = []
        score = 1.0
        
        # Temel kontroller
        if "TODO" in code:
            issues.append({"severity": "low", "message": "TODO yorumu bulundu"})
            score -= 0.05
        
        if "print(" in code and "test" not in context.get("purpose", ""):
            issues.append({"severity": "medium", "message": "Production kodda print() kullanımı"})
            score -= 0.1
        
        if "import os" in code and "system(" in code:
            issues.append({"severity": "high", "message": "Potansiyel komut enjeksiyonu riski"})
            score -= 0.3
        
        if "password" in code.lower() and "ENV" not in code:
            issues.append({"severity": "critical", "message": "Hard-coded şifre olabilir"})
            score -= 0.5
        
        score = max(0.0, score)
        return {
            "score": score,
            "issues": issues,
            "approved": score >= 0.7,
            "summary": f"{len(issues)} sorun bulundu, skor: {score:.2f}"
        }
    
    def security_scan(self, file_path: str) -> Dict:
        """Temel güvenlik taraması yapar."""
        try:
            code = open(file_path).read()
        except Exception:
            return {"approved": False, "reason": "Dosya okunamadı"}
        
        dangerous = ["eval(", "exec(", "subprocess.call", "rm -rf", "DROP TABLE", "DELETE FROM"]
        found = [d for d in dangerous if d in code]
        
        return {
            "approved": len(found) == 0,
            "dangerous_patterns": found,
            "score": 1.0 - (len(found) * 0.3),
        }