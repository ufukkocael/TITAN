# titan-core/titan/executive/attention_router.py
import asyncio
from typing import Dict, Optional, Callable
from enum import Enum

class AttentionFocus(Enum):
    OPERATOR = "operator"
    PROGRAMMER = "programmer"
    RESEARCHER = "researcher"
    COMPANION = "companion"
    ALL = "all"

class AttentionRouter:
    """Sistemin dikkatini nereye odaklayacağına karar verir."""
    
    def __init__(self):
        self.current_focus: AttentionFocus = AttentionFocus.ALL
        self.focus_history: list = []
        self.attention_budget: Dict[str, float] = {
            "operator": 0.35,
            "programmer": 0.25,
            "researcher": 0.20,
            "companion": 0.20,
        }
        self.event_handlers: Dict[str, Callable] = {}
    
    def register_handler(self, event_type: str, handler: Callable):
        """Bir olay türü için işleyici kaydet."""
        self.event_handlers[event_type] = handler
    
    def allocate_attention(self, context: Dict) -> Dict[str, float]:
        """Bağlama göre dikkat bütçesini dağıt."""
        budget = self.attention_budget.copy()
        
        # Kriz anında operator'a daha fazla dikkat
        if context.get("crisis_level", 0) > 0.7:
            budget["operator"] = 0.60
            budget["programmer"] = 0.25
            budget["researcher"] = 0.10
            budget["companion"] = 0.05
            self.current_focus = AttentionFocus.OPERATOR
        
        # Kod değişikliği sırasında programmer'a odaklan
        elif context.get("code_change_active", False):
            budget["operator"] = 0.25
            budget["programmer"] = 0.50
            budget["researcher"] = 0.15
            budget["companion"] = 0.10
            self.current_focus = AttentionFocus.PROGRAMMER
        
        # Keşif modunda researcher'a odaklan
        elif context.get("exploration_mode", False):
            budget["operator"] = 0.20
            budget["programmer"] = 0.15
            budget["researcher"] = 0.55
            budget["companion"] = 0.10
            self.current_focus = AttentionFocus.RESEARCHER
        
        # Kullanıcı etkileşiminde companion'a odaklan
        elif context.get("user_active", False):
            budget["operator"] = 0.20
            budget["programmer"] = 0.15
            budget["researcher"] = 0.10
            budget["companion"] = 0.55
            self.current_focus = AttentionFocus.COMPANION
        
        self.focus_history.append({
            "focus": self.current_focus.value,
            "budget": budget.copy(),
            "context": context,
        })
        
        # Geçmişi temiz tut
        if len(self.focus_history) > 1000:
            self.focus_history = self.focus_history[-500:]
        
        return budget
    
    async def route_event(self, event: Dict):
        """Bir olayı doğru işleyiciye yönlendir."""
        event_type = event.get("type", "unknown")
        
        if event_type in self.event_handlers:
            await self.event_handlers[event_type](event)
        else:
            # Bilinmeyen olaylar researcher'a yönlendirilir
            if "unknown" in self.event_handlers:
                await self.event_handlers["unknown"](event)
    
    def get_focus_report(self) -> Dict:
        """Mevcut odak durumunu raporla."""
        return {
            "current_focus": self.current_focus.value,
            "budget": self.attention_budget,
            "recent_history": self.focus_history[-5:],
        }