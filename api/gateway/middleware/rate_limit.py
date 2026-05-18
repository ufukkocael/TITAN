# api/gateway/middleware/rate_limit.py
import time
from collections import defaultdict
from fastapi import HTTPException, Request

class RateLimiter:
    """İstek sınırlayıcı."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests: dict[str, list] = defaultdict(list)
    
    async def check(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Pencere dışındaki istekleri temizle
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if t > now - self.window
        ]
        
        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Çok fazla istek, lütfen bekleyin.")
        
        self.requests[client_ip].append(now)