# services/companion/agents/memory_keeper.py
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

class MemoryKeeper:
    """Kullanıcıyla ilgili kişisel anıları ve tercihleri saklar."""
    
    def __init__(self, path: str = "./companion_memory"):
        self.path = Path(path)
        self.path.mkdir(exist_ok=True)
        self.user_file = self.path / "user_profile.json"
        self.conversations_file = self.path / "conversations.json"
        self._load()
    
    def _load(self):
        if self.user_file.exists():
            self.profile = json.loads(self.user_file.read_text())
        else:
            self.profile = {
                "name": "",
                "preferences": {},
                "goals": [],
                "trust_score": 0.5,
                "first_met": datetime.utcnow().isoformat(),
                "relationship_level": "acquaintance",  # acquaintance -> friend -> partner
            }
        
        if self.conversations_file.exists():
            self.conversations = json.loads(self.conversations_file.read_text())
        else:
            self.conversations = []
    
    def _save(self):
        self.user_file.write_text(json.dumps(self.profile, indent=2))
        self.conversations_file.write_text(json.dumps(self.conversations[-1000:], indent=2))
    
    def remember_conversation(self, user_message: str, titan_response: str, context: Dict = {}):
        """Bir konuşmayı kaydeder."""
        self.conversations.append({
            "timestamp": datetime.utcnow().isoformat(),
            "user": user_message,
            "titan": titan_response,
            "context": context,
        })
        if len(self.conversations) > 10000:
            self.conversations = self.conversations[-5000:]
        self._save()
    
    def update_profile(self, key: str, value):
        """Kullanıcı profilini günceller."""
        self.profile[key] = value
        self._save()
    
    def learn_preference(self, topic: str, preference: str):
        """Kullanıcının bir tercihini öğrenir."""
        self.profile["preferences"][topic] = preference
        self._save()
    
    def recall_context(self, query: str, limit: int = 5) -> List[Dict]:
        """Geçmiş konuşmalardan ilgili bağlamı getirir."""
        # Basit anahtar kelime eşleştirme
        keywords = query.lower().split()
        relevant = []
        for conv in reversed(self.conversations):
            conv_text = (conv["user"] + " " + conv["titan"]).lower()
            score = sum(1 for kw in keywords if kw in conv_text)
            if score > 0:
                relevant.append({**conv, "relevance": score})
        relevant.sort(key=lambda x: x["relevance"], reverse=True)
        return relevant[:limit]
    
    def get_relationship_status(self) -> Dict:
        """Kullanıcıyla ilişki durumunu döndürür."""
        conv_count = len(self.conversations)
        days_known = (datetime.utcnow() - datetime.fromisoformat(self.profile["first_met"])).days
        
        # İlişki seviyesini güncelle
        if conv_count > 500 and self.profile["trust_score"] > 0.8:
            self.profile["relationship_level"] = "partner"
        elif conv_count > 100 and self.profile["trust_score"] > 0.6:
            self.profile["relationship_level"] = "friend"
        
        return {
            "level": self.profile["relationship_level"],
            "conversations": conv_count,
            "days_known": days_known,
            "trust_score": self.profile["trust_score"],
        }