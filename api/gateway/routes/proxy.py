# api/gateway/routes/proxy.py
import httpx
from typing import Dict, Optional
from fastapi import HTTPException

class ServiceProxy:
    """Mikroservislere yönlendirme proxy'si."""
    
    def __init__(self, service_urls: Dict[str, str]):
        self.service_urls = service_urls
        # LLM yanıtları ve local model yüklemeleri uzun sürebileceği için 
        # timeout süresini 300 saniyeye (5 dakika) çıkarıyoruz.
        self.client = httpx.AsyncClient(timeout=300.0)
    
    async def forward(self, service: str, method: str, path: str, 
                      data: Optional[dict] = None, headers: Optional[dict] = None) -> dict:
        if service not in self.service_urls:
            raise HTTPException(status_code=404, detail=f"Servis bulunamadı: {service}")
        
        base_url = self.service_urls[service]
        url = f"{base_url}/{path.lstrip('/')}"
        
        try:
            if method == "GET":
                response = await self.client.get(url, headers=headers)
            elif method == "POST":
                response = await self.client.post(url, json=data, headers=headers)
            elif method == "PUT":
                response = await self.client.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = await self.client.delete(url, headers=headers)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text[:200]
                )
            
            return response.json() if response.text else {}
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail=f"{service} servisine bağlanılamadı")
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail=f"{service} servisi zaman aşımına uğradı (LLM yükleniyor olabilir)")
