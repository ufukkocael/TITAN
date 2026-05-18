# services/researcher/learning/replay.py
import random
from collections import deque
from typing import List, Dict

class ReplayBuffer:
    """Geçmiş deneyimleri saklar ve tekrar oynatır."""
    
    def __init__(self, max_size: int = 10000):
        self.buffer = deque(maxlen=max_size)
    
    def add(self, experience: Dict):
        self.buffer.append(experience)
    
    def sample(self, batch_size: int = 64) -> List[Dict]:
        if len(self.buffer) < batch_size:
            return list(self.buffer)
        return random.sample(list(self.buffer), batch_size)
    
    def get_successful(self, min_score: float = 0.8) -> List[Dict]:
        return [e for e in self.buffer if e.get("score", 0) >= min_score]
    
    def size(self) -> int:
        return len(self.buffer)