# titan-core/titan/agents/planner.py
from .base import BaseAgent
from typing import Dict, List

class PlannerAgent(BaseAgent):
    """Gözlemlere dayanarak görevleri planlar, önceliklendirir."""
    
    def __init__(self, config: Dict = {}):
        super().__init__("Planner", config)
        self.plans: List[Dict] = []
    
    async def observe(self, context: Dict) -> Dict:
        return context
    
    async def think(self, task: str) -> Dict:
        steps = self._decompose(task)
        return {
            "task": task,
            "steps": steps,
            "estimated_steps": len(steps),
            "priority": "high" if "kritik" in task.lower() else "normal",
        }
    
    def _decompose(self, task: str) -> List[Dict]:
        """Görevi alt görevlere böl."""
        task_lower = task.lower()
        
        if any(kw in task_lower for kw in ["hata", "crash", "çökme"]):
            return [
                {"agent": "Observer", "action": "collect_logs", "order": 1},
                {"agent": "Researcher", "action": "diagnose", "order": 2},
                {"agent": "Critic", "action": "verify_diagnosis", "order": 3},
                {"agent": "Programmer", "action": "generate_fix", "order": 4},
                {"agent": "Operator", "action": "apply_fix", "order": 5},
            ]
        elif any(kw in task_lower for kw in ["yaz", "code", "kod"]):
            return [
                {"agent": "Programmer", "action": "write_code", "order": 1},
                {"agent": "Critic", "action": "review_code", "order": 2},
                {"agent": "Programmer", "action": "test_code", "order": 3},
            ]
        elif any(kw in task_lower for kw in ["araştır", "keşfet", "analiz"]):
            return [
                {"agent": "Researcher", "action": "formulate_hypothesis", "order": 1},
                {"agent": "Researcher", "action": "run_experiment", "order": 2},
                {"agent": "Critic", "action": "evaluate_results", "order": 3},
            ]
        else:
            return [
                {"agent": "Companion", "action": "respond", "order": 1},
            ]
    
    async def act(self, plan: Dict) -> Dict:
        self.plans.append(plan)
        if len(self.plans) > 100:
            self.plans = self.plans[-50:]
        return {"status": "planned", "steps": plan.get("steps", [])}
    
    def get_recent_plans(self, n: int = 5) -> List[Dict]:
        return self.plans[-n:]