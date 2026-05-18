# titan-core/titan/executive/cognitive_scheduler.py
import asyncio
import time
from typing import Dict, List
from .priority_manager import PriorityManager, CognitiveTask, Priority
from .attention_router import AttentionRouter, AttentionFocus
from .resource_allocator import ResourceAllocator

class CognitiveScheduler:
    """TITAN'ın merkezi bilişsel zamanlayıcısı."""
    
    def __init__(self):
        self.priority_mgr = PriorityManager(max_concurrent_tasks=10)
        self.attention = AttentionRouter()
        self.resources = ResourceAllocator()
        self.running = False
        self.event_queue: List[Dict] = []
    
    async def start(self):
        """Zamanlayıcıyı başlat."""
        self.running = True
        asyncio.create_task(self._scheduler_loop())
    
    async def _scheduler_loop(self):
        """Ana zamanlayıcı döngüsü."""
        while self.running:
            try:
                # 1. Kaynak durumunu kontrol et
                resources = self.resources.get_system_resources()
                
                # 2. Bağlamı değerlendir
                context = {
                    "crisis_level": self._assess_crisis_level(),
                    "code_change_active": self._is_code_change_active(),
                    "exploration_mode": self._is_exploration_mode(),
                    "user_active": self._is_user_active(),
                }
                
                # 3. Dikkati dağıt
                budget = self.attention.allocate_attention(context)
                
                # 4. Kaynakları modlara tahsis et
                for mod, share in budget.items():
                    self.resources.allocate(
                        mod_name=mod,
                        cpu_share=share * 10,  # %10 CPU'nun payı
                        memory_mb=share * 500,  # 500MB RAM'in payı
                        priority="high" if mod == self.attention.current_focus.value else "normal"
                    )
                
                # 5. Görevleri zamanla
                tasks = self.priority_mgr.schedule()
                
                # 6. Olayları işle
                await self._process_events()
                
                await asyncio.sleep(1)  # 1 saniye bekle
            except Exception as e:
                print(f"Scheduler error: {e}")
                await asyncio.sleep(5)
    
    def _assess_crisis_level(self) -> float:
        load = self.priority_mgr.get_system_load()
        # Kuyruktaki kritik görev sayısına göre kriz seviyesi
        return min(1.0, load["queue_size"] / 100)
    
    def _is_code_change_active(self) -> bool:
        return any(t.source == "programmer" for t in self.priority_mgr.active_tasks)
    
    def _is_exploration_mode(self) -> bool:
        return self.attention.current_focus == AttentionFocus.RESEARCHER
    
    def _is_user_active(self) -> bool:
        return self.attention.current_focus == AttentionFocus.COMPANION
    
    async def _process_events(self):
        while self.event_queue:
            event = self.event_queue.pop(0)
            await self.attention.route_event(event)
    
    def submit_event(self, event: Dict):
        self.event_queue.append(event)
    
    def submit_task(self, task: CognitiveTask):
        self.priority_mgr.submit(task)
    
    def get_status(self) -> Dict:
        return {
            "scheduler": "running" if self.running else "stopped",
            "priority": self.priority_mgr.get_system_load(),
            "attention": self.attention.get_focus_report(),
            "resources": self.resources.get_allocation_report(),
        }