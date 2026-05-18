import httpx
from typing import Dict, Optional

class BrowserTool:
    """Basit HTTP istemcisi."""
    
    def __init__(self, timeout: int = 30):
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def get(self, url: str, headers: Optional[Dict] = None) -> Dict:
        try:
            response = await self.client.get(url, headers=headers)
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "content": response.text[:5000],
                "headers": dict(response.headers),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def post(self, url: str, data: Dict = {}, headers: Optional[Dict] = None) -> Dict:
        try:
            response = await self.client.post(url, json=data, headers=headers)
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "content": response.text[:2000],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}