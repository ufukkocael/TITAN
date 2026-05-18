# titan-core/titan/memory/forget.py
import time
import math
from typing import Dict, List

class ForgettingCurve:
    """Ebbinghaus unutma eğrisi uygulaması."""
    
    def __init__(self):
        # Unutma eğrisi parametreleri
        self.base_decay_rate = 0.5  # Temel unutma hızı
        self.reinforcement_bonus = 0.3  # Her tekrarda unutma yavaşlar
    
    def retention_score(self, memory_age_seconds: float, 
                       repetitions: int = 1, 
                       importance: float = 0.5) -> float:
        """Bir anının ne kadar hatırlandığını hesapla."""
        strength = 1.0 + (repetitions * self.reinforcement_bonus) + (importance * 2.0)
        retention = math.exp(-memory_age_seconds / (strength * 1000))
        return max(0.0, min(1.0, retention))
    
    def should_forget(self, memory_age_seconds: float,
                     repetitions: int = 1,
                     importance: float = 0.5,
                     threshold: float = 0.1) -> bool:
        """Bir anının silinip silinmemesi gerektiğine karar ver."""
        retention = self.retention_score(memory_age_seconds, repetitions, importance)
        return retention < threshold


class MemoryMaintenance:
    """Bellek bakım ve temizlik yöneticisi."""
    
    def __init__(self, forgetting_curve: ForgettingCurve = None):
        self.curve = forgetting_curve or ForgettingCurve()
        self.deletion_log: List[Dict] = []
    
    def cleanup_faded_memories(self, tesseract_nodes: List):
        """Tesseract düğümlerinden zayıflamış olanları temizler."""
        now = time.time()
        to_remove = []
        for node in tesseract_nodes:
            # Düğüm yaşı (varsayımsal, 0 kabul edelim şimdilik)
            # Eğer başarı skoru çok düşükse unut
            if node.success_score < 0.2:
                to_remove.append(node)
        
        for node in to_remove:
            if node in tesseract_nodes:
                tesseract_nodes.remove(node)
        
        if to_remove:
            self.deletion_log.append({
                "timestamp": now,
                "count": len(to_remove),
                "type": "tesseract_pruning"
            })
        return len(to_remove)

    def prune_episodic(self, episodic_memory, max_age_days: int = 30):
        """Epizodik bellekten eski anıları temizle."""
        now = time.time()
        pruned = 0
        for episode in list(episodic_memory.episodes):
            age = now - episode.timestamp
            if self.curve.should_forget(age, importance=episode.importance):
                if episode not in episodic_memory.milestones:
                    episodic_memory.episodes.remove(episode)
                    pruned += 1
        if pruned > 0:
            self.deletion_log.append({"timestamp": time.time(), "type": "episodic", "count": pruned})
        return pruned
    
    def prune_semantic(self, semantic_memory, min_certainty: float = 0.1):
        """Semantik bellekten düşük kesinlikli bilgileri temizle."""
        pruned = 0
        for concept in list(semantic_memory.certainty.keys()):
            if semantic_memory.get_certainty(concept) < min_certainty:
                del semantic_memory.facts[concept]
                del semantic_memory.certainty[concept]
                pruned += 1
        return pruned
