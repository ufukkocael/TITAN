# titan-core/titan/learning/distillation.py
from typing import Dict, List
import numpy as np

class SkillDistillation:
    """Başarılı deneyimleri kalıcı becerilere dönüştürür."""
    
    def __init__(self, threshold: float = 0.9):
        self.threshold = threshold
        self.skills: List[Dict] = []
    
    def distill(self, experiences: List[Dict]) -> List[Dict]:
        """Başarılı deneyimlerden beceri çıkarır."""
        new_skills = []
        
        for exp in experiences:
            if exp.get("score", 0) >= self.threshold:
                skill = {
                    "name": exp.get("type", "unknown_skill"),
                    "context": exp.get("context", {}),
                    "success_pattern": exp.get("pattern", ""),
                    "reliability": exp["score"],
                    "source": exp.get("source", "experience"),
                }
                
                # Aynı beceri zaten var mı?
                if not any(s["name"] == skill["name"] for s in self.skills):
                    self.skills.append(skill)
                    new_skills.append(skill)
        
        return new_skills
    
    def get_skills(self, min_reliability: float = 0.7) -> List[Dict]:
        return [s for s in self.skills if s["reliability"] >= min_reliability]