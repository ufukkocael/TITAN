# titan-core/titan/brain/world_model.py
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import itertools

@dataclass
class SimulationState:
    """Bir simülasyon durumu."""
    variables: Dict[str, float]
    probability: float
    utility: float

class InternalSimulator:
    """Eylem öncesi zihinsel simülasyon motoru."""
    
    def __init__(self, max_simulations: int = 1000):
        self.max_simulations = max_simulations
        self.history: List[Dict] = []
    
    def predict_outcomes(self, action: str, current_state: Dict, 
                        possible_variables: Dict[str, List[float]]) -> List[SimulationState]:
        """Bir eylemin olası sonuçlarını simüle eder."""
        simulations = []
        
        # Değişkenlerin tüm kombinasyonlarını üret
        var_names = list(possible_variables.keys())
        var_values = list(possible_variables.values())
        combinations = list(itertools.product(*var_values))
        
        # Maksimum simülasyon sayısını aşmamak için örnekle
        if len(combinations) > self.max_simulations:
            indices = np.random.choice(len(combinations), self.max_simulations, replace=False)
            combinations = [combinations[i] for i in indices]
        
        for combo in combinations:
            state = SimulationState(
                variables=dict(zip(var_names, combo)),
                probability=self._estimate_probability(combo, current_state),
                utility=self._estimate_utility(action, dict(zip(var_names, combo)), current_state),
            )
            simulations.append(state)
        
        # Olasılığa ve faydaya göre sırala
        simulations.sort(key=lambda s: s.probability * s.utility, reverse=True)
        return simulations
    
    def _estimate_probability(self, variables: tuple, current_state: Dict) -> float:
        """Bir durumun gerçekleşme olasılığını tahmin et."""
        # Geçmiş veri varsa frekans tabanlı, yoksa eşit olasılık
        if not self.history:
            return 1.0 / len(variables) if variables else 0.5
        
        similar = [h for h in self.history[-100:] 
                  if self._similarity(h["state"], current_state) > 0.7]
        
        if not similar:
            return 0.5
        
        # Benzer geçmiş durumlardan olasılık çıkar
        matching = sum(1 for s in similar if s["outcome"] == "success")
        return matching / len(similar)
    
    def _estimate_utility(self, action: str, variables: Dict, current_state: Dict) -> float:
        """Bir sonucun faydasını tahmin et."""
        # Temel fayda hesaplaması
        base_utility = 0.5
        
        # Güvenlik etkisi
        if "security" in variables:
            base_utility += variables.get("security", 0) * 0.3
        
        # Verimlilik etkisi
        if "efficiency" in variables:
            base_utility += variables.get("efficiency", 0) * 0.2
        
        # Risk cezası
        risk = variables.get("risk", 0.5)
        base_utility -= risk * 0.4
        
        return max(0.0, min(1.0, base_utility))
    
    def _similarity(self, state1: Dict, state2: Dict) -> float:
        """İki durum arasındaki benzerliği hesapla."""
        common_keys = set(state1.keys()) & set(state2.keys())
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            v1, v2 = state1[key], state2[key]
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                similarities.append(1.0 - min(abs(v1 - v2), 1.0))
            else:
                similarities.append(1.0 if v1 == v2 else 0.0)
        
        return np.mean(similarities) if similarities else 0.0
    
    def counterfactual(self, action: str, actual_outcome: Dict, 
                      alternative_action: str) -> Dict:
        """'Ya şöyle yapsaydım?' analizi yapar."""
        return {
            "action_taken": action,
            "actual_outcome": actual_outcome,
            "alternative": alternative_action,
            "estimated_utility": self._estimate_utility(alternative_action, {}, actual_outcome),
            "lesson": f"'{alternative_action}' alternatifi değerlendirilmeli.",
        }
    
    def record_outcome(self, state: Dict, action: str, outcome: str):
        """Bir eylemin sonucunu kaydet."""
        self.history.append({
            "state": state,
            "action": action,
            "outcome": outcome,
        })
        # Geçmişi sınırlı tut
        if len(self.history) > 10000:
            self.history = self.history[-5000:]