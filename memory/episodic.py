# titan-core/titan/memory/episodic.py
import time
from collections import deque
from typing import Dict, List, Optional
from datetime import datetime

class Episode:
    """Tek bir olay/deneyim kaydı."""
    def __init__(self, event: str, context: Dict, outcome: Optional[str] = None):
        self.timestamp = time.time()
        self.datetime = datetime.utcnow().isoformat()
        self.event = event
        self.context = context
        self.outcome = outcome
        self.emotional_tag: Optional[str] = None  # success, failure, neutral
        self.importance: float = 0.5

class EpisodicMemory:
    """TITAN'ın kişisel deneyim belleği. 'Ne oldu?' sorusuna cevap verir."""
    
    def __init__(self, capacity: int = 10000):
        self.episodes: deque = deque(maxlen=capacity)
        self.milestones: List[Episode] = []  # Önemli olaylar (asla silinmez)
    
    def record(self, event: str, context: Dict = {}, outcome: Optional[str] = None) -> Episode:
        """Yeni bir deneyim kaydet."""
        episode = Episode(event=event, context=context, outcome=outcome)
        
        # Önemli olayları işaretle
        if context.get("crisis_level", 0) > 0.7:
            episode.importance = 1.0
            episode.emotional_tag = "critical"
            self.milestones.append(episode)
        elif outcome == "success":
            episode.importance = 0.8
            episode.emotional_tag = "success"
        elif outcome == "failure":
            episode.importance = 0.7
            episode.emotional_tag = "failure"
        
        self.episodes.append(episode)
        return episode
    
    def recall_recent(self, n: int = 10) -> List[Episode]:
        """En son deneyimleri hatırla."""
        return list(self.episodes)[-n:]
    
    def recall_by_tag(self, tag: str, limit: int = 20) -> List[Episode]:
        """Belirli bir duygusal etikete sahip anıları getir."""
        return [e for e in self.episodes if e.emotional_tag == tag][-limit:]
    
    def recall_similar(self, event_keywords: List[str], limit: int = 5) -> List[Episode]:
        """Benzer olayları anahtar kelimelerle bul."""
        similar = []
        for ep in reversed(self.episodes):
            score = sum(1 for kw in event_keywords if kw.lower() in ep.event.lower())
            if score > 0:
                similar.append((score, ep))
        similar.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in similar[:limit]]
    
    def get_milestones(self) -> List[Episode]:
        """Kilometre taşlarını getir."""
        return self.milestones
    
    def forget_old(self, max_age_seconds: float = 86400 * 30):
        """30 günden eski düşük önemli anıları sil."""
        now = time.time()
        # deque otomatik temizler, ama milestones korunur