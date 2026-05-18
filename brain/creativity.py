# titan-core/titan/brain/creativity.py
import numpy as np
import random
from typing import List, Dict, Tuple
from ..core.tesseract import TesseractOrchestrator

class CreativityEngine:
    """Kavramsal harmanlama (Conceptual Blending) yoluyla yeni fikirler üretir."""
    
    def __init__(self, tesseract: TesseractOrchestrator):
        self.tesseract = tesseract
        self.ideas: List[Dict] = []
    
    def conceptual_blend(self, concept_a_name: str, concept_b_name: str) -> Dict:
        """İki uzak kavramı birleştirerek hibrit bir fikir oluşturur."""
        # Tesseract'tan vektörleri bul (basitleştirilmiş)
        vec_a = np.random.randn(self.tesseract.dim) 
        vec_b = np.random.randn(self.tesseract.dim)
        
        # Sentez vektörü: Rastgele ama ağırlıklı birleşim
        ratio = random.uniform(0.3, 0.7)
        blend_vec = (vec_a * ratio) + (vec_b * (1 - ratio))
        blend_vec /= (np.linalg.norm(blend_vec) + 1e-8)
        
        # Uzayda bu yeni vektöre en yakın "bilgelik" kristallerini ara
        resonances = self.tesseract.query_hyper_resonant(blend_vec, top_k=3)
        
        new_idea = {
            "name": f"Hybrid_{concept_a_name}_{concept_b_name}",
            "vector": blend_vec,
            "components": [concept_a_name, concept_b_name],
            "potential_insights": [r["concept"] for r in resonances],
            "novelty_score": random.uniform(0.7, 0.95)
        }
        self.ideas.append(new_idea)
        return new_idea

    def mutate_idea(self, idea: Dict) -> Dict:
        """Mevcut bir fikri mutasyona uğratarak geliştirir."""
        mutated_vec = idea["vector"] + np.random.normal(0, 0.05, self.tesseract.dim)
        mutated_vec /= (np.linalg.norm(mutated_vec) + 1e-8)
        
        mutated_idea = {
            "name": f"Mutated_{idea['name']}",
            "vector": mutated_vec,
            "components": idea["components"],
            "novelty_score": min(0.99, idea["novelty_score"] * 1.1),
            "generation": idea.get("generation", 0) + 1
        }
        return mutated_idea

    def run_evolutionary_cycle(self):
        """Fikirler arasında çaprazlama ve mutasyon yaparak en iyileri seçer."""
        if len(self.ideas) < 2:
            return
            
        # En iyi %50'yi seç (Novelty'ye göre)
        self.ideas.sort(key=lambda x: x["novelty_score"], reverse=True)
        survivors = self.ideas[:max(2, len(self.ideas)//2)]
        
        new_generation = []
        for i in range(len(survivors) - 1):
            # Çaprazlama
            child = self.conceptual_blend(survivors[i]["name"], survivors[i+1]["name"])
            # Mutasyon
            if np.random.rand() < 0.3:
                child = self.mutate_idea(child)
            new_generation.append(child)
            
        self.ideas.extend(new_generation)
        print(f"🧬 [CREATIVITY] Evrim döngüsü tamamlandı. {len(new_generation)} yeni fikir üretildi.")
