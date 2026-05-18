# titan-core/titan/learning/online.py
from typing import Dict, List
import time

class OnlineLearner:
    """Her etkileşimden anında öğrenir."""
    
    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate
        self.patterns: Dict[str, Dict] = {}  # desen -> {frequency, success_rate, last_seen}
        self.lessons: List[Dict] = []
    
    def learn_from_interaction(self, input_text: str, response: str, outcome: str):
        """Bir etkileşimden öğren."""
        keywords = self._extract_keywords(input_text)
        
        for kw in keywords:
            if kw not in self.patterns:
                self.patterns[kw] = {
                    "frequency": 0,
                    "successes": 0,
                    "failures": 0,
                    "last_seen": time.time(),
                }
            
            self.patterns[kw]["frequency"] += 1
            self.patterns[kw]["last_seen"] = time.time()
            
            if "success" in outcome.lower():
                self.patterns[kw]["successes"] += 1
            elif "fail" in outcome.lower():
                self.patterns[kw]["failures"] += 1
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Metinden anahtar kelimeler çıkar."""
        stopwords = {"bir", "ve", "veya", "ile", "için", "bu", "şu", "o", "ne", "nasıl"}
        words = text.lower().split()
        return [w for w in words if len(w) > 3 and w not in stopwords][:10]
    
    def get_pattern_strength(self, keyword: str) -> float:
        """Bir desenin başarı oranını getir."""
        if keyword not in self.patterns:
            return 0.0
        p = self.patterns[keyword]
        total = p["successes"] + p["failures"]
        return p["successes"] / total if total > 0 else 0.0
    
    def predict_success(self, text: str) -> float:
        """Bir girdinin başarılı olma olasılığını tahmin et."""
        keywords = self._extract_keywords(text)
        if not keywords:
            return 0.5
        
        scores = [self.get_pattern_strength(kw) for kw in keywords]
        return sum(scores) / len(scores)