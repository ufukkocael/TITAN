# titan-core/titan/integration/bus.py
import asyncio
import json
import time
from enum import Enum
from typing import Dict, Callable, List, Optional, Any
from dataclasses import dataclass, field

class EventType(Enum):
    # Operator → Diğerleri
    CRITICAL_ALERT = "critical_alert"
    SYSTEM_HEALTHY = "system_healthy"
    ANOMALY_DETECTED = "anomaly_detected"
    HEALER_ACTION = "healer_action"
    
    # Programmer → Diğerleri
    PATCH_READY = "patch_ready"
    CODE_REVIEW_REQUEST = "code_review_request"
    PR_CREATED = "pr_created"
    FIX_APPLIED = "fix_applied"
    
    # Researcher → Diğerleri
    HYPOTHESIS_READY = "hypothesis_ready"
    EXPERIMENT_RESULT = "experiment_result"
    DISCOVERY_MADE = "discovery_made"
    IMPROVEMENT_SUGGESTION = "improvement_suggestion"
    
    # Companion → Diğerleri
    USER_REQUEST = "user_request"
    USER_FEEDBACK = "user_feedback"
    RELATIONSHIP_UPDATE = "relationship_update"
    
    # Gateway → Diğerleri
    SYSTEM_START = "system_start"
    SYSTEM_SHUTDOWN = "system_shutdown"
    HEALTH_CHECK = "health_check"
    
    # Security → Diğerleri
    SECURITY_BREACH = "security_breach"
    IP_BLOCKED = "ip_blocked"
    
    # Executive → Diğerleri
    ATTENTION_REDIRECT = "attention_redirect"
    RESOURCE_REALLOCATE = "resource_reallocate"
    PRIORITY_CHANGE = "priority_change"
    CRISIS_MODE = "crisis_mode"

@dataclass
class Message:
    id: str
    type: EventType
    source: str
    target: Optional[str]  # None = broadcast
    payload: Dict
    timestamp: float = field(default_factory=time.time)
    correlation_id: Optional[str] = None  # İstek-yanıt eşleştirme

class MessageBus:
    """TITAN'ın merkezi sinir sistemi. Tüm modlar arası iletişimi sağlar."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_history: List[Message] = []
        self.pending_responses: Dict[str, asyncio.Event] = {}
        self.response_data: Dict[str, Dict] = {}
        self.running = False
    
    def subscribe(self, event_type: Any, callback: Callable):
        """Bir olay türüne abone ol (Enum veya string kabul eder)."""
        key = event_type.value if hasattr(event_type, 'value') else str(event_type)
        if key not in self.subscribers:
            self.subscribers[key] = []
        self.subscribers[key].append(callback)
    
    def subscribe_all(self, callback: Callable):
        """Tüm olaylara abone ol."""
        self.subscribe("*", callback)
    
    async def publish(self, message: Message):
        """Bir mesajı yayınla."""
        self.message_history.append(message)
        
        # Hedef varsa sadece ona, yoksa herkese
        targets = [message.target] if message.target else None
        
        # Belirli olay türüne abone olanlara gönder
        key = message.type.value
        if key in self.subscribers:
            for callback in self.subscribers[key]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(message)
                    else:
                        callback(message)
                except Exception as e:
                    print(f"Bus error ({key}): {e}")
        
        # Tüm olaylara abone olanlara gönder
        if "*" in self.subscribers:
            for callback in self.subscribers["*"]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(message)
                    else:
                        callback(message)
                except Exception as e:
                    print(f"Bus error (*): {e}")
        
        # Geçmişi sınırlı tut
        if len(self.message_history) > 10000:
            self.message_history = self.message_history[-5000:]
    
    async def request(self, target: str, event_type: EventType, payload: Dict, timeout: float = 30.0) -> Optional[Dict]:
        """İstek gönder ve yanıt bekle."""
        correlation_id = f"req_{int(time.time() * 1000)}"
        message = Message(
            id=f"msg_{correlation_id}",
            type=event_type,
            source="bus",
            target=target,
            payload=payload,
            correlation_id=correlation_id,
        )
        
        event = asyncio.Event()
        self.pending_responses[correlation_id] = event
        
        await self.publish(message)
        
        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
            return self.response_data.pop(correlation_id, None)
        except asyncio.TimeoutError:
            self.pending_responses.pop(correlation_id, None)
            return None
    
    def respond(self, correlation_id: str, response: Dict):
        """Bir isteğe yanıt ver."""
        self.response_data[correlation_id] = response
        if correlation_id in self.pending_responses:
            self.pending_responses[correlation_id].set()
    
    def get_recent_events(self, event_type: Optional[EventType] = None, limit: int = 50) -> List[Message]:
        """Son olayları getir."""
        events = self.message_history
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]
    
    def get_stats(self) -> Dict:
        return {
            "total_events": len(self.message_history),
            "active_subscribers": sum(len(v) for v in self.subscribers.values()),
            "pending_requests": len(self.pending_responses),
            "event_types": list(set(m.type.value for m in self.message_history[-100:])),
        }