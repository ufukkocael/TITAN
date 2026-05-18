# services/researcher/agents/critic.py
from typing import Dict, List

class ResearchCritic:
    """Araştırma sonuçlarını değerlendirir, hakem denetimi yapar."""
    
    def review_hypothesis(self, hypothesis: Dict) -> Dict:
        """Bir hipotezi değerlendirir."""
        issues = []
        score = 1.0
        
        # Temel bilimsel kontroller
        if hypothesis.get("confidence", 0) < 0.3:
            issues.append("Çok düşük güven skoru, daha fazla kanıt gerekli.")
            score -= 0.3
        
        if len(hypothesis.get("tests", [])) == 0:
            issues.append("Hiç test edilmemiş.")
            score -= 0.5
        
        if hypothesis.get("status") == "rejected":
            # Reddedilen hipotez bile değerlidir
            issues.append("Reddedilmiş hipotez - negatif sonuç da bilgidir.")
            score -= 0.1
        
        return {
            "score": max(0.0, score),
            "issues": issues,
            "approved": score >= 0.6,
            "recommendation": "Onaylandı" if score >= 0.6 else "Daha fazla test gerekli."
        }
    
    def peer_review(self, discovery: Dict, existing_knowledge: List[Dict] = []) -> Dict:
        """Keşfi mevcut bilgiyle karşılaştırarak hakem denetimi yapar."""
        # Benzer keşif var mı?
        similar = []
        for existing in existing_knowledge:
            if existing.get("question", "").lower() in discovery.get("question", "").lower():
                similar.append(existing)
        
        if similar:
            return {
                "novel": False,
                "similar_to": [s.get("id") for s in similar],
                "recommendation": "Bu keşif daha önce yapılmış olabilir."
            }
        
        return {
            "novel": True,
            "recommendation": "Orijinal keşif. Yayınlanabilir."
        }