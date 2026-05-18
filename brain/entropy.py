# titan-core/titan/brain/entropy.py
import numpy as np
import time
from typing import Dict, List

class NeuralEntropyManager:
    """TITAN'ın zihnindeki karmaşayı (entropi) yöneten ve sinaptik budama yapan katman."""
    
    def __init__(self, tesseract):
        self.tesseract = tesseract
        self.pruning_threshold = 0.2
        self.entropy_level = 0.0
        self.last_clean_up = time.time()

    def measure_entropy(self) -> float:
        """Tesseract uzayındaki düğümlerin düzensizliğini ölçer."""
        if not self.tesseract.nodes: return 0.0
        
        # Başarı skorlarının varyansı entropi göstergesidir
        scores = [n.success_score for n in self.tesseract.nodes]
        self.entropy_level = np.var(scores) if len(scores) > 1 else 0.0
        return self.entropy_level

    def synaptic_pruning(self) -> int:
        """Düşük performanslı ve kullanılmayan düğümleri silerek zihni berraklaştırır."""
        initial_count = len(self.tesseract.nodes)
        
        # Sabit çapalar (Anchors) asla silinmez
        keepers = []
        for node in self.tesseract.nodes:
            if node.concept in ["RAW_DATA", "MEMORY", "LOGIC_GATE", "WISDOM", "OVERSOUL"]:
                keepers.append(node)
                continue
            
            # Başarı skoru ve aktivasyon frekansına göre karar ver
            if node.success_score > self.pruning_threshold or node.activation_count > 5:
                keepers.append(node)
        
        self.tesseract.nodes = keepers
        pruned_count = initial_count - len(keepers)
        
        if pruned_count > 0:
            print(f"🧹 [ENTROPY] Sinaptik budama tamamlandı. {pruned_count} zayıf düğüm silindi.")
        
        return pruned_count

    def get_clarity_report(self) -> Dict:
        return {
            "entropy_level": self.entropy_level,
            "cognitive_clarity": 1.0 - self.entropy_level,
            "active_synapses": len(self.tesseract.nodes)
        }
