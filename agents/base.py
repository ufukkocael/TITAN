# titan-core/titan/agents/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time


class BaseAgent(ABC):
    """Tüm TITAN ajanları için soyut temel sınıf."""
    
    def __init__(self, name: str, config: Dict = {}):
        self.name = name
        self.config = config
        self.state = "idle"
        self.last_action_time = time.time()
        self.action_count = 0
        self.tools: Dict[str, Any] = {}
    
    @abstractmethod
    async def observe(self, context: Dict) -> Dict:
        """Durumu gözlemle ve iç temsilini güncelle."""
        pass
    
    @abstractmethod
    async def think(self, task: str) -> Dict:
        """Görev üzerinde düşün, bir plan veya çözüm üret."""
        pass
    
    @abstractmethod
    async def act(self, plan: Dict) -> Dict:
        """Planı eyleme dök."""
        pass
    
    def register_tool(self, name: str, tool: Any):
        """Ajana bir araç kaydet."""
        self.tools[name] = tool
    
    def get_status(self) -> Dict:
        """Ajanın durumunu döndür."""
        return {
            "name": self.name,
            "state": self.state,
            "action_count": self.action_count,
            "tools": list(self.tools.keys()),
            "uptime": time.time() - self.last_action_time,
        }
    
    async def run(self, task: str, context: Dict = {}) -> Dict:
        """Ajanın ana çalışma döngüsü."""
        self.state = "observing"
        observation = await self.observe(context)
        
        self.state = "thinking"
        plan = await self.think(task)
        
        self.state = "acting"
        result = await self.act(plan)
        
        self.action_count += 1
        self.last_action_time = time.time()
        self.state = "idle"
        
        return {
            "observation": observation,
            "plan": plan,
            "result": result,
        }