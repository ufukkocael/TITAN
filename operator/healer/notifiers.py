# services/operator/healer/notifiers.py
import httpx
from datetime import datetime

class SlackNotifier:
    def __init__(self, webhook_url: str = ""):
        self.webhook_url = webhook_url
    
    async def send(self, title: str, message: str, severity: str = "warning") -> bool:
        if not self.webhook_url:
            return False
        colors = {"critical": "#FF0000", "warning": "#FFA500", "info": "#36A64F", "resolved": "#36A64F"}
        payload = {
            "attachments": [{
                "color": colors.get(severity, "#CCC"),
                "title": title,
                "text": message,
                "footer": f"TITAN Operator • {datetime.utcnow().isoformat()}",
            }]
        }
        async with httpx.AsyncClient() as c:
            try:
                r = await c.post(self.webhook_url, json=payload, timeout=10)
                return r.status_code == 200
            except Exception:
                return False