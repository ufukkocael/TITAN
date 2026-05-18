# titan-core/titan/stability/event_guard.py
from typing import Dict, List, Any
import time


class EventGuard:
    """Olay akışını denetleyen koruma katmanı."""
    
    # Tehlikeli olay tipleri
    DANGEROUS_EVENTS = [
        "delete_all", "drop_database", "shutdown_force",
        "format_disk", "kill_process"
    ]
    
    # Rate limit için
    def __init__(self, max_events_per_second: int = 100):
        self.processed_events: List[Dict] = []
        self.event_counters: Dict[str, int] = {}
        self.last_reset = time.time()
        self.max_events_per_second = max_events_per_second
    
    def validate_event(self, event: Dict) -> bool:
        """Bir olayın geçerli ve güvenli olup olmadığını kontrol et."""
        event_type = event.get("type", "unknown")
        
        # 1. Tehlikeli olay kontrolü
        if event_type in self.DANGEROUS_EVENTS:
            return False
        
        # 2. Rate limit kontrolü
        now = time.time()
        if now - self.last_reset > 1.0:
            self.event_counters.clear()
            self.last_reset = now
        
        self.event_counters[event_type] = self.event_counters.get(event_type, 0) + 1
        total_events = sum(self.event_counters.values())
        
        if total_events > self.max_events_per_second:
            return False
        
        # 3. Olay boyutu kontrolü
        if len(str(event)) > 100000:  # 100KB
            return False
        
        return True
    
    def log_event(self, event: Dict):
        """İşlenen olayı logla."""
        self.processed_events.append({
            "timestamp": time.time(),
            "event": event,
            "validated": self.validate_event(event)
        })
        
        # Geçmişi sınırlı tut
        if len(self.processed_events) > 10000:
            self.processed_events = self.processed_events[-5000:]
    
    def get_stats(self) -> Dict:
        """İstatistikleri döndür."""
        return {
            "total_events": len(self.processed_events),
            "event_types": dict(self.event_counters),
            "dangerous_blocked": sum(
                1 for e in self.processed_events 
                if e.get("event", {}).get("type") in self.DANGEROUS_EVENTS
            )
        }