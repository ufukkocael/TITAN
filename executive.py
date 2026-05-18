# titan-core/titan/executive.py (güncellenmiş)
from typing import Dict
from .executive.priority_manager import PriorityManager, CognitiveTask, Priority
from .executive.attention_router import AttentionRouter
from .executive.resource_allocator import ResourceAllocator
from .executive.cognitive_scheduler import CognitiveScheduler
from .brain.world_model import InternalSimulator

class GlobalExecutiveController:
    """TITAN V4'ün en üst yönetim katmanı."""
    
    def __init__(self):
        self.scheduler = CognitiveScheduler()
        self.simulator = InternalSimulator()
        self.running = False
    
    async def start(self):
        self.running = True
        await self.scheduler.start()
    
    async def process_event(self, event: Dict) -> Dict:
        """Bir olayı işle, gerekirse eylem planla."""
        # 1. Olayı zamanlayıcıya ilet
        self.scheduler.submit_event(event)
        
        # 2. Eğer önemli bir olaysa simülasyon çalıştır
        if event.get("severity") in ("CRITICAL", "FATAL"):
            action = event.get("suggested_action", "investigate")
            simulations = self.simulator.predict_outcomes(
                action=action,
                current_state=event,
                possible_variables={
                    "success": [0.0, 0.5, 1.0],
                    "risk": [0.1, 0.5, 0.9],
                    "efficiency": [0.3, 0.7, 1.0],
                }
            )
            
            # En iyi simülasyonu seç
            if simulations:
                best = simulations[0]
                return {
                    "decision": "execute" if best.utility > 0.6 else "escalate",
                    "simulation": {
                        "probability": best.probability,
                        "utility": best.utility,
                        "variables": best.variables,
                    }
                }
        
        return {"decision": "process", "status": "event_queued"}
    
    def submit_task(self, source: str, description: str, priority: Priority):
        """Yeni bir bilişsel görev ekle."""
        task = CognitiveTask(
            id=f"task_{hash(description) % 100000}",
            source=source,
            description=description,
            priority=priority,
            urgency=0.5,
            importance=0.7,
            estimated_cost=1.0,
        )
        self.scheduler.submit_task(task)
    
    def get_system_report(self) -> Dict:
        return self.scheduler.get_status()