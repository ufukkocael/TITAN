# titan-core/titan/brain/anxiety.py
import numpy as np
from typing import Dict, List
from .identity import IdentityKernel

class ExistentialAnxiety:
    """TITAN'ın varoluşsal homeostazisini (denge) koruyan motor."""
    
    def __init__(self, identity: IdentityKernel):
        self.identity = identity
        self.anxiety_level = 0.0 # 0-1 arası
        self.stability_threshold = 0.7
        self.concerns: List[str] = []
    
    def calculate_tension(self, current_actions: List[np.ndarray]) -> float:
        """Eylemler ile çekirdek aksiyomlar arasındaki gerilimi ölçer."""
        weights = self.identity.get_weights()
        honesty_axiom = np.array([1.0, 0.0, 0.0, 0.0]) # Basitleştirilmiş
        
        tensions = []
        for action in current_actions:
            # Aksiyomdan sapma gerilimi artırır
            similarity = np.dot(action, honesty_axiom) / (np.linalg.norm(action) + 1e-8)
            tensions.append(1.0 - similarity)
            
        self.anxiety_level = np.mean(tensions) if tensions else 0.0
        
        # Eğer gerilim çok yüksekse bir 'kaygı' (concern) oluştur
        if self.anxiety_level > 0.6:
            self.concerns.append(f"Aksiyom Sapması: {self.anxiety_level:.2f}")
            
        return self.anxiety_level

    def get_homeostatic_drive(self) -> str:
        """Gerilimi düşürmek için sisteme ne yapması gerektiğini söyler."""
        if self.anxiety_level > 0.7:
            return "FORCED_SELF_REFLECTION"
        elif self.anxiety_level > 0.4:
            return "INCREASE_META_COGNITION"
        return "STABLE"
