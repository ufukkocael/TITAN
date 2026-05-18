# titan-core/titan/learning/vault.py
import json
import os
from datetime import datetime
from typing import Dict, List

class LearningVault:
    """TITAN'ın kendi modelini eğitmek için topladığı 'Altın Veri' deposu."""
    
    def __init__(self, storage_path: str = "./data/training_set.jsonl"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
    def store_interaction(self, prompt: str, response: str, success_score: float):
        """Başarılı bir etkileşimi eğitim verisi olarak kaydeder."""
        if success_score < 0.8: return # Sadece yüksek kaliteli veriyi sakla
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "instruction": prompt,
            "output": response,
            "quality": success_score
        }
        
        try:
            with open(self.storage_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            print(f"📈 [LEARNING-VAULT] Yeni eğitim verisi arşivlendi.")
        except: pass

    def get_stats(self) -> Dict:
        if not os.path.exists(self.storage_path): return {"size": 0}
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return {"total_samples": len(lines)}
