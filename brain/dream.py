# titan-core/titan/brain/dream.py
import asyncio
import random
import time
from typing import List, Dict
from titan.core.tesseract import TesseractOrchestrator
from titan.brain.creativity import CreativityEngine

class DreamLayer:
    """TITAN'ın boşta kaldığında (idle) bilgi işleme ve konsolidasyon katmanı."""
    
    def __init__(self, tesseract: TesseractOrchestrator, creativity: CreativityEngine):
        self.tesseract = tesseract
        self.creativity = creativity
        self.dream_history: List[Dict] = []
        self.is_dreaming = False
    
    async def initiate_rem_phase(self, duration_seconds: int = 30):
        """Hızlı Bilgi İşleme (REM) fazını başlatır."""
        self.is_dreaming = True
        
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            all_nodes = self.tesseract.nodes
            if len(all_nodes) > 5:
                node_a = random.choice(all_nodes)
                node_b = random.choice(all_nodes)
                
                if node_a.concept != node_b.concept:
                    try:
                        dream_insight = self.creativity.conceptual_blend(node_a.concept, node_b.concept)
                        self.dream_history.append({
                            "timestamp": time.time(),
                            "nodes": [node_a.concept, node_b.concept],
                            "insight": dream_insight["name"]
                        })
                    except: pass
            
            await asyncio.sleep(2)
            
        self.is_dreaming = False

    def get_latent_insights(self) -> List[str]:
        return [d["insight"] for d in self.dream_history[-10:]]
