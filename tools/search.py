# titan-core/titan/tools/search.py
import httpx
import asyncio
from typing import List, Dict, Optional
import re

class SearchTool:
    """TITAN'ın internet üzerinde bilgi taraması yapmasını sağlayan araç."""
    
    def __init__(self, timeout: int = 20):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        self.timeout = timeout
    
    async def search(self, query: str, limit: int = 5) -> List[Dict]:
        """DuckDuckGo üzerinden arama yapar ve sonuçları döner."""
        try:
            url = f"https://lite.duckduckgo.com/lite/?q={query.replace(' ', '+')}"
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                resp = await client.get(url)
                
                if resp.status_code != 200:
                    return [{"error": f"Search failed with status {resp.status_code}", "source": "DuckDuckGo"}]
                
                results = []
                html = resp.text
                
                # Basit Regex ile sonuçları ayıkla
                matches = re.findall(r'<a[^>]+class="result-link"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
                snippets = re.findall(r'<td class="result-snippet">(.*?)</td>', html, re.DOTALL)
                
                for i, (link, title) in enumerate(matches[:limit]):
                    clean_title = re.sub(r'<[^>]+>', '', title).strip()
                    snippet = snippets[i] if i < len(snippets) else "Özet bulunamadı."
                    clean_snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                    
                    results.append({
                        "title": clean_title,
                        "url": link if link.startswith('http') else f"https:{link}",
                        "snippet": clean_snippet,
                        "rank": i + 1
                    })
                    
                return results
        except Exception as e:
            return [{"error": f"{e}", "source": "SearchTool"}]
