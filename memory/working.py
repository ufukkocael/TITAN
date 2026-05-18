# titan-core/titan/memory/working.py
from collections import deque
from typing import Dict, List, Optional, Any
import time

class WorkingMemory:
    """TITAN'ın kısa vadeli çalışma belleği. 'Şu an ne düşünüyorum?' sorusuna cevap verir."""
    
    def __init__(self, capacity: int = 7):  # Miller Yasası: 7±2
        self.capacity = capacity
        self.items: deque = deque(maxlen=capacity)
        self.focus: Optional[str] = None
        self.context: Dict = {}
        self.last_updated = time.time()
    
    def hold(self, item: Any, label: str = ""):
        """Çalışma belleğine bir öğe ekle."""
        entry = {
            "item": item,
            "label": label,
            "timestamp": time.time(),
        }
        self.items.append(entry)
        self.last_updated = time.time()
    
    def set_focus(self, label: str):
        """Dikkati belirli bir öğeye odakla."""
        self.focus = label
        self.last_updated = time.time()
    
    def get_focus(self) -> Optional[str]:
        """Şu anki odak konusunu getir."""
        return self.focus
    
    def get_all(self) -> List[Dict]:
        """Tüm aktif öğeleri getir."""
        return list(self.items)
    
    def get_by_label(self, label: str) -> Optional[Dict]:
        """Etikete göre öğe getir."""
        for item in self.items:
            if item["label"] == label:
                return item
        return None
    
    def clear(self):
        """Çalışma belleğini temizle."""
        self.items.clear()
        self.focus = None
        self.context = {}
        self.last_updated = time.time()
    
    def is_full(self) -> bool:
        return len(self.items) >= self.capacity
    
    def get_age(self) -> float:
        """En son güncellemeden bu yana geçen süre."""
        return time.time() - self.last_updated
    
    def update_context(self, key: str, value: Any):
        """Bağlam bilgisini güncelle."""
        self.context[key] = value
        self.last_updated = time.time()
    
    def get_context(self) -> Dict:
        return self.context