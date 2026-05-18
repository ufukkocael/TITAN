# titan-core/titan/agents/observer.py
from .base import BaseAgent
from typing import Dict
import asyncio
import time


class ObserverAgent(BaseAgent):
    """Sistemden ve kullanıcıdan gelen sinyalleri izler, özetler."""
    
    def __init__(self, config: Dict = {}):
        super().__init__("Observer", config)
        self.observations: list = []
    
    async def observe(self, context: Dict) -> Dict:
        """Durumu gözlemle."""
        logs = context.get("recent_logs", [])
        alerts = context.get("alerts", [])
        user_input = context.get("user_input", "")
        
        observation = {
            "log_count": len(logs),
            "active_alerts": len(alerts),
            "user_intent": user_input,
            "anomaly_score": min(len(logs) / 100, 1.0),
            "timestamp": time.time(),
        }
        
        self.observations.append(observation)
        if len(self.observations) > 1000:
            self.observations = self.observations[-500:]
        
        return observation
    
    async def think(self, task: str) -> Dict:
        """Gözlem stratejisi belirle."""
        return {"action": "observe", "target": task, "priority": "high"}
    
    async def act(self, plan: Dict) -> Dict:
        """Gözlemi uygula."""
        return {"status": "observed", "data": plan}
    
    def get_trend(self, metric: str = "anomaly_score") -> str:
        """Bir metriğin trendini analiz et."""
        if len(self.observations) < 2:
            return "stable"
        
        recent = self.observations[-10:]
        values = [o.get(metric, 0) for o in recent]
        
        if len(values) >= 2:
            if values[-1] > values[0] * 1.2:
                return "rising"
            elif values[-1] < values[0] * 0.8:
                return "falling"
        
        return "stable"