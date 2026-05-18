# titan-core/titan/executive/resource_allocator.py
import psutil
import time
from typing import Dict, Optional

class ResourceAllocator:
    """Sistem kaynaklarını modlar arasında dağıtır."""
    
    def __init__(self, max_memory_percent: float = 80.0, max_cpu_percent: float = 90.0):
        self.max_memory = max_memory_percent
        self.max_cpu = max_cpu_percent
        self.allocations: Dict[str, Dict] = {}
        self.resource_history: list = []
    
    def get_system_resources(self) -> Dict:
        """Mevcut sistem kaynaklarını ölç."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "disk_percent": psutil.disk_usage('/').percent,
        }
    
    def can_allocate(self, mod_name: str, cpu_needed: float, memory_mb: float) -> bool:
        """Bir mod için kaynak ayrılabilir mi?"""
        resources = self.get_system_resources()
        
        if resources["cpu_percent"] + cpu_needed > self.max_cpu:
            return False
        
        if resources["memory_percent"] + (memory_mb / 1024 * 100 / psutil.virtual_memory().total) > self.max_memory:
            return False
        
        return True
    
    def allocate(self, mod_name: str, cpu_share: float, memory_mb: float, priority: str = "normal") -> bool:
        """Bir moda kaynak ayır."""
        if not self.can_allocate(mod_name, cpu_share, memory_mb):
            # Yüksek öncelikli ise düşük öncelikli tahsisleri serbest bırak
            if priority == "critical":
                self._free_low_priority_resources(memory_mb)
            else:
                return False
        
        self.allocations[mod_name] = {
            "cpu_share": cpu_share,
            "memory_mb": memory_mb,
            "priority": priority,
            "allocated_at": time.time(),
        }
        return True
    
    def _free_low_priority_resources(self, needed_memory_mb: float):
        """Düşük öncelikli tahsisleri serbest bırak."""
        freed = 0
        for mod in sorted(self.allocations.keys(), 
                         key=lambda m: 0 if self.allocations[m]["priority"] == "low" else 1):
            if self.allocations[mod]["priority"] in ("low", "background"):
                freed += self.allocations[mod]["memory_mb"]
                del self.allocations[mod]
                if freed >= needed_memory_mb:
                    break
    
    def get_allocation_report(self) -> Dict:
        """Kaynak tahsis raporu."""
        resources = self.get_system_resources()
        return {
            "system": resources,
            "allocations": self.allocations,
            "total_allocated_cpu": sum(a["cpu_share"] for a in self.allocations.values()),
            "total_allocated_memory_mb": sum(a["memory_mb"] for a in self.allocations.values()),
        }