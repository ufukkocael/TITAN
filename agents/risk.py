# titan-core/titan/agents/risk.py
from .base import BaseAgent
from typing import Dict, List
import asyncio


class RiskAgent(BaseAgent):
    """Risk analizi yapar, 'Ya şöyle olursa?' sorularını cevaplar."""
    
    def __init__(self, config: Dict = {}):
        super().__init__("Risk", config)
        self.risk_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.85,
        }
    
    async def observe(self, context: Dict) -> Dict:
        """Risk durumunu gözlemle."""
        return context
    
    async def think(self, task: str) -> Dict:
        """Risk analizi yap."""
        return self.assess_risk(task)
    
    async def act(self, plan: Dict) -> Dict:
        """Risk değerlendirmesine göre aksiyon al."""
        action = plan.get("action", "")
        risk_level = self.assess_risk(action)
        
        if risk_level["level"] == "high":
            return {"status": "blocked", "reason": "Risk çok yüksek", "risk": risk_level}
        elif risk_level["level"] == "medium":
            return {"status": "warning", "risk": risk_level, "requires_approval": True}
        return {"status": "approved", "risk": risk_level}
    
    def assess_risk(self, action: str) -> Dict:
        """Bir eylemin risk seviyesini değerlendir."""
        action_lower = action.lower()
        
        risk_score = 0.0
        factors = []
        
        if any(kw in action_lower for kw in ["delete", "sil", "format", "drop"]):
            risk_score += 0.5
            factors.append("Veri silme riski")
        
        if any(kw in action_lower for kw in ["kernel", "system", "root"]):
            risk_score += 0.4
            factors.append("Sistem seviyesi değişiklik")
        
        if any(kw in action_lower for kw in ["rollback", "downgrade"]):
            risk_score += 0.3
            factors.append("Geri alma riski")
        
        if any(kw in action_lower for kw in ["restart", "reboot"]):
            risk_score += 0.2
            factors.append("Hizmet kesintisi")
        
        risk_score = min(1.0, risk_score)
        
        level = "low"
        if risk_score >= self.risk_thresholds["high"]:
            level = "high"
        elif risk_score >= self.risk_thresholds["medium"]:
            level = "medium"
        
        return {
            "level": level,
            "score": risk_score,
            "factors": factors,
            "blast_radius": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low",
        }
    
    def simulate_blast_radius(self, action: str, affected_services: List[str]) -> Dict:
        """Bir eylemin etki alanını simüle et."""
        risk = self.assess_risk(action)
        
        impact = {
            "affected_services": len(affected_services),
            "estimated_downtime_seconds": len(affected_services) * 30 if risk["level"] == "high" else len(affected_services) * 5,
            "rollback_possible": "rollback" not in action.lower(),
        }
        
        return {**risk, "impact": impact}