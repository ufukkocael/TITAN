# titan-core/titan/predictive.py
import time
from collections import defaultdict

class PredictiveEngine:
    def __init__(self, window_seconds: int = 600, threshold: int = 10):
        self.window = window_seconds
        self.threshold = threshold
        self.counts: dict[str, list] = defaultdict(list)
    
    def feed(self, platform: str, severity: str, message: str) -> dict | None:
        if severity not in ("FATAL", "CRITICAL", "ERROR"):
            return None
        now = time.time()
        self.counts[platform].append((now, message))
        cutoff = now - self.window
        self.counts[platform] = [(t, m) for t, m in self.counts[platform] if t > cutoff]
        count = len(self.counts[platform])
        if count >= self.threshold:
            return {"alert": True, "platform": platform, "count": count,
                    "message": f"{platform}: {count} kritik hata ({self.window}s)"}
        return None