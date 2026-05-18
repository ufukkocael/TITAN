# titan-core/titan/executive/meta_goal.py
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid

class GoalType(Enum):
    STABILITY = "stability"
    GROWTH = "growth"
    EXPLORATION = "exploration"
    SECURITY = "security"
    EFFICIENCY = "efficiency"

class GoalStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"

@dataclass
class Goal:
    id: str
    description: str
    goal_type: GoalType
    priority: float = 0.5
    status: GoalStatus = GoalStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    progress: float = 0.0

class MetaGoalEngine:
    """TITAN'ın otonom hedef yönetim motoru."""
    
    def __init__(self, governance_guard=None):
        self.guard = governance_guard
        self.goals: Dict[str, Goal] = {}
        self._init_core_goals()
    
    def _init_core_goals(self):
        core = [("Sistem Kararlılığı", GoalType.STABILITY, 1.0),
                ("Kullanıcı Güveni", GoalType.SECURITY, 0.9)]
        for desc, gtype, prio in core:
            gid = str(uuid.uuid4())[:8]
            self.goals[gid] = Goal(id=gid, description=desc, goal_type=gtype, priority=prio)
    
    def generate_goal(self, observation: str, context: Dict, goal_type: GoalType) -> Optional[Goal]:
        # GOVERNANCE CHECK (Goal Drift Koruması)
        if self.guard:
            check = self.guard.validate_goal(observation, context.get("priority", 0.5))
            if not check["approved"]:
                print(f"🛑 [GOAL] Hedef reddedildi: {check['reason']}")
                return None
        
        goal = Goal(
            id=str(uuid.uuid4())[:8],
            description=observation[:100],
            goal_type=goal_type,
            priority=context.get("priority", 0.5)
        )
        self.goals[goal.id] = goal
        return goal

    def introspect(self) -> Dict:
        active = [g for g in self.goals.values() if g.status == GoalStatus.ACTIVE]
        top = sorted(active, key=lambda x: x.priority, reverse=True)
        return {
            "total_goals": len(self.goals),
            "active_goals": len(active),
            "top_priorities": [{"description": g.description} for g in top[:3]]
        }
