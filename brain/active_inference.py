# titan-core/titan/brain/active_inference.py
import numpy as np
from typing import Dict, List

class ActiveInferenceEngine:
    """Belirsizliği azaltmak için dünyayı aktif olarak sorgulayan merak motoru."""
    
    def __init__(self, world_model):
        self.world_model = world_model
        self.surprise_history: List[float] = []
        self.free_energy = 1.0 # Minimize edilmeye çalışılan değer
    
    def calculate_surprise(self, predicted_state: Dict, actual_state: Dict) -> float:
        """Tahmin ile gerçeklik arasındaki farkı (sürpriz) ölçer."""
        diffs = []
        for k in set(predicted_state.keys()) & set(actual_state.keys()):
            if isinstance(predicted_state[k], (int, float)) and isinstance(actual_state[k], (int, float)):
                diffs.append(abs(predicted_state[k] - actual_state[k]))
        
        surprise = np.mean(diffs) if diffs else 0.0
        self.surprise_history.append(surprise)
        # Serbest enerjiyi güncelle
        self.free_energy = (self.free_energy * 0.9) + (surprise * 0.1)
        return surprise

    def generate_epistemic_action(self) -> Dict:
        """Belirsizliği azaltmak için 'bilgi toplama' (merak) eylemi üretir."""
        if self.free_energy > 0.5:
            return {
                "type": "EPISTEMIC_PROBE",
                "target": "high_uncertainty_zone",
                "priority": "HIGH",
                "reason": f"Yüksek Serbest Enerji ({self.free_energy:.2f}) tespiti."
            }
        return {"type": "IDLE", "reason": "Sistem dengede."}
