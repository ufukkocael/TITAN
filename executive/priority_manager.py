# titan-core/titan/executive/priority_manager.py
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np

class Priority(Enum):
    CRITICAL = 0   # Sistem çöküşü, güvenlik ihlali
    HIGH = 1       # Performans düşüşü, kullanıcı etkisi
    MEDIUM = 2     # Optimizasyon, iyileştirme
    LOW = 3        # Keşif, araştırma
    BACKGROUND = 4 # Uzun vadeli öğrenme

@dataclass
class CognitiveTask:
    id: str
    source: str           # Hangi moddan geldiği
    description: str
    priority: Priority
    urgency: float        # 0-1, zamanla artar
    importance: float     # 0-1, sistem etkisi
    estimated_cost: float # Kaynak maliyeti
    deadline: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    
    def effective_priority(self) -> float:
        """Acil ve önemli görevler önce gelir."""
        # priority.value: 0(CRITICAL) -> 5, 4(BACKGROUND) -> 1
        priority_multiplier = (5 - self.priority.value)
        urgency_factor = 1.0 + (self.urgency * 2.0)
        importance_factor = 1.0 + (self.importance * 3.0)
        cost_penalty = 1.0 / (self.estimated_cost + 0.1)
        
        # Deadline yaklaşıyorsa aciliyet katlanarak artar
        if self.deadline:
            time_left = max(0, self.deadline - time.time())
            deadline_factor = 1.0 + (1.0 / (time_left + 1.0)) * 10.0
        else:
            deadline_factor = 1.0
        
        return priority_multiplier * urgency_factor * importance_factor * cost_penalty * deadline_factor

class PriorityManager:
    """Küresel bilişsel önceliklendirme motoru."""
    
    def __init__(self, max_concurrent_tasks: int = 10):
        self.max_concurrent = max_concurrent_tasks
        self.task_queue: List[CognitiveTask] = []
        self.active_tasks: List[CognitiveTask] = []
        self.completed_tasks: List[Dict] = []
        self.mod_stats: Dict[str, Dict] = {}
    
    def submit(self, task: CognitiveTask):
        """Yeni bir bilişsel görev ekle."""
        self.task_queue.append(task)
        
        # Mod istatistiklerini güncelle
        if task.source not in self.mod_stats:
            self.mod_stats[task.source] = {"submitted": 0, "completed": 0, "starved": 0}
        self.mod_stats[task.source]["submitted"] += 1
    
    def schedule(self) -> List[CognitiveTask]:
        """En yüksek öncelikli görevleri seç."""
        # Görevleri efektif önceliğe göre sırala
        self.task_queue.sort(key=lambda t: t.effective_priority(), reverse=True)
        
        # Maksimum eşzamanlı görev sayısına göre seç
        selected = self.task_queue[:self.max_concurrent]
        
        # Açlık kontrolü: çok bekleyen düşük öncelikli görevleri yükselt
        now = time.time()
        for task in self.task_queue:
            if task not in selected and (now - task.created_at) > 300:  # 5 dakika
                task.priority = Priority(task.priority.value - 1) if task.priority.value > 0 else task.priority
                self.mod_stats[task.source]["starved"] += 1
        
        self.active_tasks = selected
        return selected
    
    def complete(self, task_id: str, result: Dict):
        """Bir görevi tamamlandı olarak işaretle."""
        for task in self.active_tasks:
            if task.id == task_id:
                self.completed_tasks.append({
                    "task": task.description,
                    "source": task.source,
                    "result": result,
                    "completed_at": time.time(),
                })
                self.active_tasks.remove(task)
                self.mod_stats[task.source]["completed"] += 1
                break
        
        # Tamamlanan görevleri kuyruktan temizle
        self.task_queue = [t for t in self.task_queue if t.id != task_id]
    
    def get_system_load(self) -> Dict:
        """Sistem yük durumunu raporla."""
        return {
            "queue_size": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "max_concurrent": self.max_concurrent,
            "load_percentage": len(self.active_tasks) / self.max_concurrent * 100,
            "mod_stats": self.mod_stats,
        }