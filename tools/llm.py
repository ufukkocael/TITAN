# titan-core/titan/tools/llm.py
import os
import json
import httpx

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", default_model="llama3.2:3b"):
        self.base_url = base_url
        self.default_model = default_model
        self.timeout = 300.0 # 5 dakika (Yavaş sistemler için artırıldı)
    
    async def _request(self, method, endpoint, **kwargs):
        target_url = f"{self.base_url}{endpoint}"
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        async with httpx.AsyncClient(timeout=self.timeout, limits=limits) as client:
            try:
                if method == "GET":
                    response = await client.get(target_url, **kwargs)
                else:
                    response = await client.post(target_url, **kwargs)
                
                if response.status_code == 200:
                    return response.json()
                return {"error": f"Ollama error {response.status_code}"}
            except httpx.ReadTimeout:
                return {"error": "Ollama zaman aşımına uğradı. Model yükleniyor olabilir."}
            except Exception as e:
                return {"error": f"Bağlantı hatası: {e}"}

    async def is_running(self):
        try:
            res = await self._request("GET", "/api/tags")
            return "error" not in res
        except: return False

    async def list_models(self):
        res = await self._request("GET", "/api/tags")
        if "error" in res: return []
        return [m["name"] for m in res.get("models", [])]

    async def generate(self, prompt, system=None, **kwargs):
        payload = {
            "model": kwargs.get("model", self.default_model),
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_ctx": 4096}
        }
        if system: payload["system"] = system
        result = await self._request("POST", "/api/generate", json=payload)
        return {"response": result.get("response", "") or result.get("error", "Error")}
    
    async def chat(self, messages, **kwargs):
        payload = {
            "model": kwargs.get("model", self.default_model),
            "messages": messages,
            "stream": False
        }
        result = await self._request("POST", "/api/chat", json=payload)
        msg_obj = result.get("message", {})
        return {"response": msg_obj.get("content", "") or result.get("error", "Error")}

class GroqClient:
    def __init__(self, api_key=None, default_model="llama-3.1-8b-instant"):
        self.api_key = api_key
        self.default_model = default_model
        self.base_url = "https://api.groq.com/openai/v1"
        self.timeout = 60.0
    
    async def chat(self, messages, **kwargs):
        if not self.api_key: return {"response": "❌ Groq Key Missing", "error": True}
        headers = {"Authorization": f"Bearer {self.api_key.strip()}", "Content-Type": "application/json"}
        clean_msgs = []
        for m in messages:
            try:
                r = f"{m.get('role', 'user')}"
                c = f"{m.get('content', '')}".strip()
                if c: clean_msgs.append({"role": r, "content": c})
            except: pass
        if not clean_msgs: return {"response": "❌ No messages", "error": True}
        payload = {
            "model": kwargs.get("model", self.default_model),
            "messages": clean_msgs,
            "temperature": 0.7,
            "max_tokens": 2048
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                if response.status_code == 200:
                    return {"response": response.json()["choices"][0]["message"]["content"], "error": False}
                return {"response": f"❌ Groq API Error {response.status_code}", "error": True}
        except Exception as e:
            return {"response": f"❌ Connection Error: {e}", "error": True}

class LLMGateway:
    def __init__(self, config):
        self.config = config
        self.provider = config.get("provider", "ollama")
        self.ollama = OllamaClient(
            base_url=config.get("ollama_url", "http://localhost:11434"),
            default_model=config.get("ollama_model", "llama3.2:3b")
        )
        self.groq = None
        self.use_ollama = self.provider == "ollama"
        self.use_groq = self.provider == "groq"
    
    async def ask(self, prompt, context="", **kwargs):
        system_msg = f"Sen TITAN V4'sün. Geliştiricin U.KOCAEL. Bağlam: {context}"
        try:
            if self.use_groq and self.groq:
                res = await self.groq.chat([{"role":"system","content":system_msg},{"role":"user","content":prompt}], **kwargs)
                return res.get("response", "Error")
            res = await self.ollama.generate(prompt, system=system_msg, **kwargs)
            return res.get("response", "Error")
        except Exception as e:
            return f"❌ [LLM] Error: {e}"

    async def chat(self, messages, **kwargs):
        try:
            if self.use_groq and self.groq:
                res = await self.groq.chat(messages, **kwargs)
                return res.get("response", "Error")
            res = await self.ollama.chat(messages, **kwargs)
            return res.get("response", "Error")
        except Exception as e:
            return f"❌ [LLM] Error: {e}"

    async def is_ollama_running(self): return await self.ollama.is_running()
    async def list_ollama_models(self): return await self.ollama.list_models()
    def get_status(self): return {"provider": self.provider, "groq_available": self.groq is not None}
