# titan-core/titan/learning/self_improve.py
from typing import Dict, List
import datetime

class SelfImprovement:
    """TITAN'ın kendi kodunu ve parametrelerini optimize etmesi."""
    
    IMMUTABLE_AXIOMS = ["HONESTY"]  # Asla değiştirilemez
    
    def __init__(self, identity_kernel=None):
        self.identity = identity_kernel
        self.improvement_history: List[Dict] = []
    
    def evaluate_change(self, proposed_change: Dict) -> Dict:
        """Bir öz-iyileştirme değişikliğini değerlendirir."""
        target = proposed_change.get("target", "")
        new_value = proposed_change.get("new_value", 0)
        
        # Değişmez aksiyomlar kontrolü
        if target in self.IMMUTABLE_AXIOMS:
            return {
                "approved": False,
                "reason": f"{target} değişmez bir aksiyomdur. Değiştirilemez.",
                "harmonic_score": 0.0,
            }
        
        # Harmonik skor hesaplama (basitleştirilmiş)
        honesty_score = 1.0 if target != "HONESTY" else 0.0
        risk = abs(new_value - proposed_change.get("old_value", 0.5))
        
        harmonic_score = honesty_score * 0.6 + (1.0 - risk) * 0.4
        
        return {
            "approved": harmonic_score > 0.7,
            "reason": "Harmonik skor yeterli" if harmonic_score > 0.7 else "Harmonik skor çok düşük",
            "harmonic_score": harmonic_score,
            "risk_level": "low" if risk < 0.2 else "medium" if risk < 0.5 else "high",
        }
    
    def apply_improvement(self, change: Dict) -> Dict:
        """Onaylanmış bir iyileştirmeyi uygular."""
        evaluation = self.evaluate_change(change)
        
        if not evaluation["approved"]:
            return {"status": "rejected", **evaluation}
        
        self.improvement_history.append({
            **change,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "evaluation": evaluation,
        })
        
        return {
            "status": "applied",
            "target": change["target"],
            "old_value": change.get("old_value"),
            "new_value": change["new_value"],
            "harmonic_score": evaluation["harmonic_score"],
        }
    
    def get_improvement_suggestions(self, performance_data: Dict) -> List[Dict]:
        """Performans verisine göre iyileştirme önerileri üretir."""
        suggestions = []
        
        if performance_data.get("efficiency", 1.0) < 0.7:
            suggestions.append({
                "target": "EFFICIENCY",
                "old_value": 0.10,
                "new_value": 0.12,
                "reason": "Verimlilik skoru düşük, ağırlığı artır.",
            })
        
        if performance_data.get("learning_rate", 0.01) < 0.005:
            suggestions.append({
                "target": "LEARNING",
                "old_value": 0.05,
                "new_value": 0.07,
                "reason": "Öğrenme hızı çok yavaş, ağırlığı artır.",
            })
        
        return suggestions