# titan-core/titan/stability/deadlock_detector.py
from dataclasses import dataclass
from typing import List, Dict, Set
import time
import threading


@dataclass
class DeadlockReport:
    thread_id: str
    detected_at: float
    description: str
    resources: List[str]


class DeadlockDetector:
    """Kilitlenme tespiti yapar."""
    
    def __init__(self):
        self.lock_history: List[Dict] = []
        self.active_locks: Dict[str, str] = {}  # resource -> thread_id
        self.waiting_threads: Dict[str, List[str]] = {}  # thread_id -> [resources]
    
    def register_lock(self, resource: str, thread_id: str):
        """Bir kilidi kaydet."""
        if resource in self.active_locks:
            self.waiting_threads.setdefault(thread_id, []).append(resource)
        else:
            self.active_locks[resource] = thread_id
    
    def release_lock(self, resource: str, thread_id: str):
        """Bir kilidi serbest bırak."""
        if resource in self.active_locks and self.active_locks[resource] == thread_id:
            del self.active_locks[resource]
        
        # Bekleyen thread'leri kontrol et
        for tid, resources in list(self.waiting_threads.items()):
            if resource in resources:
                resources.remove(resource)
                if not resources:
                    del self.waiting_threads[tid]
    
    def check(self) -> List[DeadlockReport]:
        """Kilitlenme kontrolü yap."""
        reports = []
        
        # Basit döngü tespiti
        for thread_id, waiting_for in self.waiting_threads.items():
            for resource in waiting_for:
                if resource in self.active_locks:
                    owner = self.active_locks[resource]
                    if owner in self.waiting_threads:
                        # Potansiyel deadlock
                        reports.append(DeadlockReport(
                            thread_id=thread_id,
                            detected_at=time.time(),
                            description=f"Thread {thread_id} waiting for {resource} held by {owner}",
                            resources=waiting_for
                        ))
        
        self.lock_history.append({
            "timestamp": time.time(),
            "active_locks": len(self.active_locks),
            "waiting_threads": len(self.waiting_threads),
            "deadlocks": len(reports)
        })
        
        # Geçmişi sınırlı tut
        if len(self.lock_history) > 1000:
            self.lock_history = self.lock_history[-500:]
        
        return reports