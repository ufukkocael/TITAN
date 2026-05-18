# titan-core/titan/bridge.py
import numpy as np
from .core.tesseract import TesseractOrchestrator
from .memory.vault import WisdomVault


class TitanBridge:
    """Tesseract ile WisdomVault arasında köprü."""
    
    def __init__(self, orchestrator: TesseractOrchestrator, memory_path: str = "./titan_memory"):
        self.orchestrator = orchestrator
        self.vault = WisdomVault(path=memory_path)
    
    async def ingest(self, log_entry: dict):
        """Bir log girdisini işle ve Tesseract'a ekle."""
        text = f"{log_entry.get('severity','')} {log_entry.get('message','')}"
        vector = np.random.randn(384)
        
        past = self.vault.recall(vector)
        
        initial_w = 0.0
        if past and past.get('distances') and len(past['distances']) > 0:
            if len(past['distances'][0]) > 0 and past['distances'][0][0] < 0.2:
                initial_w = 0.5
        
        node = self.orchestrator.add_node(
            concept=log_entry.get('message', '')[:80],
            vector=vector,
            w=initial_w
        )
        self.orchestrator.apply_w_gravity()
        return node
    
    async def ask_oversoul(self, question: str) -> dict:
        """Oversoul'a soru sor."""
        q_vec = np.random.randn(384)
        results = self.orchestrator.query_hyper_resonant(q_vec, top_k=3)
        if not results:
            return {"root_cause": "unknown", "confidence": 0.0}
        top = results[0]
        return {
            "root_cause": top["concept"],
            "confidence": top["score"],
            "action": "rollback" if top["score"] > 0.9 else "investigate"
        }