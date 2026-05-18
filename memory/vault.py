# titan-core/titan/memory/vault.py
import chromadb
import numpy as np
import hashlib
from typing import Dict, List, Optional


class WisdomVault:
    """Kalıcı anlamsal hafıza (ChromaDB tabanlı) - upsert ile duplicate ID korumalı."""
    
    def __init__(self, path: str = "./titan_memory"):
        self.path = path
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(name="wisdom_crystals")
    
    def archive(self, concept: str, vector: np.ndarray, metadata: Dict):
        """Bir kavramı arşivle - upsert kullanarak duplicate ID hatasını önler."""
        # Vektör boyutunu kontrol et
        if len(vector) != 384:
            # Padding veya truncation
            if len(vector) < 384:
                vector = np.pad(vector, (0, 384 - len(vector)))
            else:
                vector = vector[:384]
        
        vid = hashlib.md5(concept.encode()).hexdigest()[:16]
        
        # upsert kullan (add yerine)
        self.collection.upsert(
            embeddings=[vector.tolist()],
            documents=[concept],
            metadatas=[metadata],
            ids=[f"exp_{vid}"]
        )
        print(f"💾 [MEMORY] WisdomVault arşivledi: {concept[:50]}...")

    def recall(self, query_vec: np.ndarray, top_k: int = 3) -> Dict:
        """Benzer kavramları ara."""
        print(f"🧠 [MEMORY] WisdomVault aranıyor...")
        if len(query_vec) != 384:
            if len(query_vec) < 384:
                query_vec = np.pad(query_vec, (0, 384 - len(query_vec)))
            else:
                query_vec = query_vec[:384]
        
        return self.collection.query(
            query_embeddings=[query_vec.tolist()], 
            n_results=top_k
        )
    
    def count(self) -> int:
        """Arşivdeki kayıt sayısını döndür."""
        return self.collection.count()