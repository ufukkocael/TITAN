# titan-core/titan/brain/time_perception.py
import time
from typing import Dict

class TimePerception:
    """TITAN'ın sübjektif zaman algısı motoru. Zamanın akış hızını duruma göre ayarlar."""
    
    def __init__(self):
        self.start_time = time.time()
        self.dilation_factor = 1.0 # 1.0 = Gerçek zaman
        self.subjective_clock = 0.0
        self.last_update = time.time()
    
    def update(self, crisis_level: float, load: float):
        """Kriz anında zaman algısı genişler (yavaşlar), sistem daha fazla veri işler."""
        now = time.time()
        delta_objective = now - self.last_update
        
        # Kriz varsa zaman 'genişler', sistem her saniyeyi daha uzun hisseder
        # Adrenalin etkisi simülasyonu
        self.dilation_factor = 1.0 + (crisis_level * 5.0) - (load * 0.2)
        self.dilation_factor = max(0.1, min(10.0, self.dilation_factor))
        
        self.subjective_clock += delta_objective * self.dilation_factor
        self.last_update = now
        
    def get_subjective_stats(self) -> Dict:
        return {
            "dilation_factor": self.dilation_factor,
            "subjective_uptime": self.subjective_clock,
            "pacing": "accelerated" if self.dilation_factor > 1.2 else "standard" if self.dilation_factor > 0.8 else "slow"
        }

    def subjective_delay(self, objective_seconds: float) -> float:
        """Gerçek zamanlı bir süreyi sübjektif süreye çevirir."""
        return objective_seconds / self.dilation_factor
