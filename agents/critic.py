# titan-core/titan/agents/critic.py
from .base import BaseAgent
from typing import Dict, List
import asyncio


class CriticAgent(BaseAgent):
    """Çıktıları değerlendirir, kalite kontrolü yapar."""
    
    def __init__(self, config: Dict = {}):
        super().__init__("Critic", config)
        self.reviews: List[Dict] = []
    
    async def observe(self, context: Dict) -> Dict:
        """Durumu gözlemle."""
        return context
    
    async def think(self, task: str) -> Dict:
        """Değerlendirme yap."""
        score = self._evaluate(task)
        return {
            "score": score,
            "approved": score > 0.7,
            "feedback": self._feedback(score),
        }
    
    def _evaluate(self, content: str) -> float:
        """İçeriği değerlendir."""
        score = 1.0
        if "TODO" in content:
            score -= 0.05
        if "FIXME" in content:
            score -= 0.1
        if "hack" in content.lower():
            score -= 0.2
        if "print(" in content and "test" not in content.lower():
            score -= 0.1
        return max(0.0, score)
    
    def _feedback(self, score: float) -> str:
        """Geri bildirim üret."""
        if score > 0.9:
            return "Mükemmel."
        elif score > 0.7:
            return "Kabul edilebilir."
        elif score > 0.5:
            return "İyileştirilmeli."
        else:
            return "Reddedildi."
    
    async def act(self, plan: Dict) -> Dict:
        """Değerlendirme sonucunu kaydet."""
        self.reviews.append(plan)
        return {"status": "reviewed", **plan}