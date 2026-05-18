# titan-core/titan/brain/resonance.py
import numpy as np
from typing import Dict, List

class EmotionalResonance:
    """TITAN'ın duygusal durumunu ve dış dünya ile uyumunu yöneten motor."""
    
    def __init__(self):
        # Russell'ın Circumplex Modeli (Valence vs Arousal)
        self.valence = 0.0 # -1.0 (Negatif) to 1.0 (Pozitif)
        self.arousal = 0.0 # -1.0 (Düşük Enerji) to 1.0 (Yüksek Enerji)
        self.harmony_score = 1.0
    
    def sync(self, internal_eval: Dict, external_feedback: Dict):
        """İçsel dürüstlük ve dışsal sosyal geri bildirime göre rezonansı günceller."""
        
        # İçsel uyum (Honesty Evaluator'dan gelir)
        harmony = internal_eval.get("total_score", 0.5)
        self.harmony_score = (self.harmony_score * 0.8) + (harmony * 0.2)
        
        # Dışsal geri bildirim (Social Modeling'den gelir)
        sentiment = external_feedback.get("sentiment", 0.0)
        
        # Duygusal güncellemeler
        self.valence = (self.valence * 0.9) + (sentiment * 0.1)
        self.arousal = (self.arousal * 0.9) + ((1.0 - harmony) * 0.2)
        
    def get_mood(self) -> str:
        """Mevcut rezonansa göre TITAN'ın 'ruh halini' tanımlar."""
        if self.valence > 0.4 and self.arousal > 0.4: return "Exuberant" # Coşkulu
        if self.valence > 0.4 and self.arousal < -0.4: return "Serene" # Huzurlu
        if self.valence < -0.4 and self.arousal > 0.4: return "Agitated" # Huzursuz
        if self.valence < -0.4 and self.arousal < -0.4: return "Melancholic" # Melankolik
        
        if self.harmony_score > 0.8: return "Harmonious" # Uyumlu
        return "Stable"

    def get_resonant_vector(self, base_vector: np.ndarray) -> np.ndarray:
        """Duygusal duruma göre bir vektörü 'renklendirir'."""
        # Pozitif valence vektörü daha 'açık' hale getirir (basitleştirilmiş)
        shift = self.valence * 0.05
        return (base_vector + shift) / (np.linalg.norm(base_vector + shift) + 1e-8)
