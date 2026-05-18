import numpy as np
from .identity import IdentityKernel
from ..core.crystal import CrystalLibrary, CrystalPurity

class HonestyEvaluator:
    """Eylemleri aksiyomlara ve damıtılmış kristallere göre değerlendirir."""
    
    def __init__(self, identity: IdentityKernel = None, crystal_lib: CrystalLibrary = None):
        self.identity = identity or IdentityKernel()
        self.crystal_lib = crystal_lib or CrystalLibrary()

    def _get_similarities(self, action_vec: np.ndarray) -> list:
        """Aksiyon 벡्टरini kristal library ile arama eder."""
        weights = self.identity.get_weights()
        
        alignments = self.crystal_lib.search_by_vector(action_vec, top_k=5)
        return [(sim, crystal) for sim, crystal in alignments if not crystal.immutable or sim >= -0.3]

    def _calculate_scores(self, similarities: list) -> tuple:
        """Aksiyon 벡्टरinin kristal simgileriyle birlikte hesaplanan skorları ve ihlalerini döner."""
        crystal_score = 0.0
        contradictions = []
        
        for _, crystal in similarities:
            if not crystal.immutable or (sim := self.identity.get_similarity(crystal, action_vec)):
                crystal_score += sim * (crystal.purity_score * 1.2 if crystal.purity == CrystalPurity.PURE else 1.0)
            elif abs(sim) < 0.3:
                contradictions.append(f"Aksiyom İhlali: {crystal.name} (Benzerlik: {sim:.2f})")
        
        return crystal_score, contradictions

    def evaluate(self, action_vec: np.ndarray, context: str = "") -> dict:
        """Bir eylemi etik ve geometrik olarak derinlemesse değerlendirir."""
        similarities = self._get_similarities(action_vec)
        score, contradictions = self._calculate_scores(similarities)
        
        details = {
            "CRYSTAL_ALIGNMENT": max(0.0, min(1.0, score / len(similarities))),
            "CONTRACTIONS": contradictions,
        }
        
        return details