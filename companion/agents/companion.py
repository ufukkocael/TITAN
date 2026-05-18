# services/companion/agents/companion.py
import random
import json
import re
from typing import Dict, Optional, Any
from datetime import datetime
from .memory_keeper import MemoryKeeper
from titan.tools.llm import LLMGateway, GroqClient


class CompanionAgent:
    """Kullanıcıyla doğal etkileşim kuran ana ajan."""
    
    GREETINGS = {
        "morning": ["Günaydın! Bugün nasıl hissediyorsun?", "Sabah enerjini gördüm, harika bir gün olacak."],
        "afternoon": ["İyi günler! Öğle arası iyi geçti mi?", "Günün bu saati genelde en üretken zamanındır."],
        "evening": ["İyi akşamlar! Bugün neler başardık?", "Akşam yorgunluğunu hissediyorum, sana bir kahve yapayım mı?"],
        "night": ["Gece geç saatlere kadar çalışıyorsun. Dinlenmeyi unutma.", "Uyku moduna geçmeden önce son bir şey var mı?"],
    }
    
    def __init__(self, config: Dict):
        self.name = config.get("name", "TITAN")
        self.personality = config.get("personality", "warm_professional")
        self.memory = MemoryKeeper()
        self.config = config
        
        # LLM Gateway
        llm_config = config.get("llm", {
            "provider": "ollama",
            "ollama_url": "http://localhost:11434",
            "ollama_model": "llama3.2:3b"
        })
        self.llm = LLMGateway(llm_config)
        self.ollama_available = False
    
    async def initialize(self):
        """Ollama bağlantısını kontrol et."""
        try:
            self.ollama_available = await self.llm.is_ollama_running()
            if self.ollama_available:
                models = await self.llm.list_ollama_models()
                print(f"🦙 Ollama bağlandı! Mevcut modeller: {models}")
            else:
                print("⚠️ Ollama çalışmıyor.")
        except Exception as e:
            print(f"⚠️ Ollama bağlantı hatası: {e}")
    
    def _get_greeting(self) -> str:
        hour = datetime.utcnow().hour + 3
        if 6 <= hour < 12:
            return random.choice(self.GREETINGS["morning"])
        elif 12 <= hour < 17:
            return random.choice(self.GREETINGS["afternoon"])
        elif 17 <= hour < 22:
            return random.choice(self.GREETINGS["evening"])
        else:
            return random.choice(self.GREETINGS["night"])
    
    async def respond(self, user_message, llm_provider=None, llm_api_key=None):
        """Kullanıcı mesajına yanıt üretir."""
        
        # LLM Gateway parametrelerini güncelle
        if llm_provider:
            self.llm.provider = llm_provider
            self.llm.use_ollama = (llm_provider == "ollama")
            self.llm.use_groq = (llm_provider == "groq")
            if llm_provider == "groq" and llm_api_key:
                self.llm.groq = GroqClient(api_key=llm_api_key)

        user_lower = user_message.lower()
        relationship = self.memory.get_relationship_status()
        
        # 1. İnternet Araştırması Tetikleyicisi
        search_triggers = ["araştır", "internette bul", "nedir", "kimdir", "haber", "güncel"]
        if any(trigger in user_lower for trigger in search_triggers):
            import httpx
            # Temizlik
            topic = user_message
            for t in search_triggers: topic = topic.replace(t, "")
            topic = topic.strip("? .!").strip()
            
            if len(topic) > 2:
                try:
                    print(f"🌍 [COMPANION] İnternet araştırması başlatılıyor: {topic}")
                    async with httpx.AsyncClient(timeout=40.0) as client:
                        # Researcher modülüne Gateway üzerinden git
                        resp = await client.post(
                            "http://localhost:9000/api/researcher/api/web-research",
                            json={"observation": topic}
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            if data.get("findings"):
                                first = data["findings"][0]
                                reply = f"🔍 İnternette senin için araştırdım:\n\n**{first['title']}**\n\n{first['summary'][:400]}...\n\n🔗 Kaynak: {first['url']}"
                                self.memory.remember_conversation(user_message, reply)
                                return {"response": reply, "tone": "intelligent"}
                except Exception as e:
                    print(f"❌ Araştırma hatası: {e}")

        # 2. Selamlaşma
        if any(word in user_lower for word in ["merhaba", "selam", "günaydın", "iyi akşamlar"]):
            greeting = self._get_greeting()
            if relationship["days_known"] > 0:
                name = self.memory.profile.get('name', 'dostum')
                greeting = f"Merhaba {name}! {greeting}"
            self.memory.remember_conversation(user_message, greeting)
            return {"response": greeting, "tone": "warm"}
        
        # 3. LLM Entegrasyonu
        try:
            recent_context = self.memory.recall_context(user_message, limit=3)
            context_str = json.dumps(recent_context, ensure_ascii=False)[:500]
            
            messages = [
                {"role": "system", "content": f"Sen TITAN V4'sün. Geliştiricin U.KOCAEL. Kişiliğin: {self.personality}."},
                {"role": "user", "content": f"Bağlam: {context_str}\n\nKullanıcı: {user_message}"}
            ]
            
            response_text = await self.llm.chat(messages, temperature=0.7)
            self.memory.remember_conversation(user_message, response_text)
            return {"response": response_text, "tone": "intelligent"}
            
        except Exception as e:
            print(f"LLM hatası: {e}")
            return {"response": f"Bir hata oluştu: {e}", "tone": "error"}
