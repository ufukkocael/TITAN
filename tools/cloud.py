# titan-core/titan/cloud.py
import hashlib
import os
import numpy as np
from typing import Dict, Optional, List
import httpx
import asyncio

class WisdomExchangeClient:
    """Yerel TITAN ile Merkezi Katedral (SaaS) arasındaki senkronizasyon ajanı."""
    
    def __init__(self, local_vault=None, central_url: Optional[str] = None, fallback_urls: Optional[List[str]] = None):
        self.vault = local_vault
        env_url = os.environ.get("TITAN_CENTRAL_URL")
        self.central_url = central_url or env_url or "https://api.titan-net.io"
        self.fallback_urls = fallback_urls or []
        self.active_urls = [self.central_url] + [u for u in self.fallback_urls if u != self.central_url]
        self.client = httpx.AsyncClient(timeout=30.0)
        self.sync_status = {"last_sync": 0, "blueprints_shared": 0, "vaccines_received": 0}
    
    def _anonymize(self, concept: str, vector: np.ndarray, metadata: Dict) -> Dict:
        """Ham veriyi anonim bir 'Bilgelik Şablonu'na dönüştürür."""
        symptom_hash = hashlib.sha256(concept.encode()).hexdigest()[:16]
        anonymized_vector = (vector + np.random.normal(0, 0.01, vector.shape)).tolist()
        
        return {
            "blueprint_id": f"bp_{symptom_hash}",
            "symptom_signature": symptom_hash,
            "anonymized_vector": anonymized_vector,
            "solution": metadata.get("solution", "unknown"),
            "platform": metadata.get("platform", "generic"),
            "w_score": metadata.get("w", 0.8),
            "timestamp": metadata.get("timestamp", ""),
        }
    
    async def _request(self, method: str, path: str, **kwargs):
        last_error = None
        for url in self.active_urls:
            full_url = f"{url.rstrip('/')}{path}"
            try:
                if method == "get":
                    response = await self.client.get(full_url, **kwargs)
                elif method == "post":
                    response = await self.client.post(full_url, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                if response.status_code < 500:
                    return response
                last_error = Exception(f"Server error {response.status_code} at {full_url}")
            except Exception as e:
                last_error = e
                print(f"⚠️ [CLOUD] [REQUEST] {type(self).__name__} hatası: {type(e).__name__}: {e} ({full_url})")
                continue
        if last_error:
            raise last_error
        return None

    async def share_wisdom(self, concept: str, vector: np.ndarray, metadata: Dict) -> bool:
        """Yerel bir başarıyı merkezi sunucuya gönder."""
        blueprint = self._anonymize(concept, vector, metadata)
        try:
            response = await self._request(
                "post",
                "/api/v1/blueprint",
                json=blueprint
            )
            if response and response.status_code == 201:
                self.sync_status["blueprints_shared"] += 1
                self.sync_status["last_sync"] = __import__('time').time()
                return True
        except Exception as e:
            print(f"⚠️ [CLOUD] share_wisdom hata: {type(e).__name__}: {e}")
        return False
    
    async def fetch_vaccines(self, environment: str = "all", limit: int = 20) -> List[Dict]:
        """Merkezi sunucudan aşıları çeker."""
        try:
            response = await self._request(
                "get",
                "/api/v1/vaccines",
                params={"env": environment, "limit": limit}
            )
            if response and response.status_code == 200:
                vaccines = response.json()
                self.sync_status["vaccines_received"] += len(vaccines)
                self.sync_status["last_sync"] = __import__('time').time()
                return vaccines
        except Exception as e:
            print(f"⚠️ [CLOUD] fetch_vaccines hata: {type(e).__name__}: {e}")
        return []
    
    async def apply_vaccines(self):
        """Çekilen aşıları yerel WisdomVault'a kaydeder."""
        vaccines = await self.fetch_vaccines()
        if self.vault:
            for v in vaccines:
                self.vault.archive(
                    concept=v.get('symptom_signature', 'unknown'),
                    vector=np.array(v.get('anonymized_vector', [])),
                    metadata={
                        "solution": v.get('solution', ''),
                        "platform": v.get('platform', ''),
                        "w": v.get('w_score', 0.8),
                        "source": "global_vaccine",
                    }
                )
        return len(vaccines)
    
    async def health_check(self) -> Dict:
        """Merkezi sunucuya bağlantı kontrolü."""
        # Try each active URL with a small retry/backoff in case the mock server is still coming up.
        for url in self.active_urls:
            full_path = f"{url.rstrip('/')}/health"
            attempt = 0
            while attempt < 3:
                try:
                    response = await self.client.get(full_path, timeout=5.0)
                    ok = response is not None and response.status_code == 200
                    if ok:
                        return {"connected": True, "url": url}
                    else:
                        print(f"⚠️ [CLOUD] health_check non-200 from {url}: {response.status_code}")
                        break
                except Exception as e:
                    attempt += 1
                    wait = 0.5 * (2 ** (attempt - 1))
                    print(f"⚠️ [CLOUD] health_check attempt {attempt} for {url} failed: {type(e).__name__}: {e} - retrying in {wait}s")
                    await asyncio.sleep(wait)
                    continue

        print(f"⚠️ [CLOUD] health_check hata: tüm endpointler erişilemedi: {self.active_urls}")
        return {"connected": False, "url": self.central_url}