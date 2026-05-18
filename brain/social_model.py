# titan-core/titan/brain/social_model.py
from typing import Dict, List, Optional
import numpy as np

class EntityState:
    """Bir dış varlığın (insan veya yapay zeka) tahmini durumu."""
    def __init__(self, name: str):
        self.name = name
        self.trust_score = 0.5
        self.estimated_mood = "neutral"
        self.knowledge_level = 0.5
        self.interaction_count = 0

class SocialBrain:
    """Zihin Teorisi (Theory of Mind) uygulayan sosyal modelleme motoru."""
    
    def __init__(self):
        self.entities: Dict[str, EntityState] = {}
    
    def model_entity(self, name: str, behavior_log: List[Dict]) -> EntityState:
        """Dış varlığın davranışlarından bir profil çıkarır."""
        if name not in self.entities:
            self.entities[name] = EntityState(name)
        
        entity = self.entities[name]
        
        # Basit duygu ve güven analizi
        positive_actions = sum(1 for b in behavior_log if b.get("sentiment") == "positive")
        total_actions = len(behavior_log) if behavior_log else 1
        
        entity.trust_score = (entity.trust_score * 0.7) + ((positive_actions / total_actions) * 0.3)
        entity.interaction_count += total_actions
        
        if entity.trust_score > 0.8:
            entity.estimated_mood = "cooperative"
        elif entity.trust_score < 0.3:
            entity.estimated_mood = "adversarial"
            
        return entity

    def predict_reaction(self, entity_name: str, action_description: str) -> Dict:
        """Sistemin bir eylemine karşı varlığın nasıl tepki vereceğini tahmin eder."""
        entity = self.entities.get(entity_name, EntityState("unknown"))
        
        # Riskli bir eylem ve düşük güven varsa negatif tepki bekle
        if "delete" in action_description.lower() and entity.trust_score < 0.5:
            return {"predicted_response": "alarmed", "resistance_probability": 0.9}
        
        return {"predicted_response": "accepting", "resistance_probability": 0.1}
