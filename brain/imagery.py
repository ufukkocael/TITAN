# titan-core/titan/brain/imagery.py
import numpy as np
from typing import List, Dict, Tuple

class MentalCanvas:
    """TITAN'ın içsel görselleştirme alanı (Zihin Gözü)."""
    
    def __init__(self, resolution: int = 64):
        self.res = resolution
        # Kavramların uzaysal izdüşümü
        self.canvas = np.zeros((resolution, resolution))
        self.spatial_map: Dict[str, Tuple[int, int]] = {}
    
    def project_concept(self, concept_name: str, vector: np.ndarray):
        """Bir vektörü 2D düzleme izdüşürerek imge oluşturur."""
        # Basit boyut indirgeme (Vektörün ilk 2 elemanı koordinat olarak kullanılır)
        x = int(((vector[0] + 1) / 2) * (self.res - 1))
        y = int(((vector[1] + 1) / 2) * (self.res - 1))
        
        x = max(0, min(self.res - 1, x))
        y = max(0, min(self.res - 1, y))
        
        self.canvas[x, y] = 1.0 # İmgeyi çiz
        self.spatial_map[concept_name] = (x, y)
        # print(f"👁️ [IMAGERY] '{concept_name}' imgelendi: ({x}, {y})")

    def get_mental_layout(self) -> Dict:
        """Kavramların zihindeki uzaysal dizilimini döndürür."""
        return self.spatial_map

    def find_spatial_patterns(self) -> List[str]:
        """Zihinde birbirine yakın imgelenen kavramları (ilişkileri) bulur."""
        patterns = []
        concepts = list(self.spatial_map.keys())
        for i in range(len(concepts)):
            for j in range(i + 1, len(concepts)):
                c1, c2 = concepts[i], concepts[j]
                p1, p2 = self.spatial_map[c1], self.spatial_map[c2]
                dist = np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
                
                if dist < (self.res * 0.1): # Yakınlık eşiği
                    patterns.append(f"Görsel İlişki: {c1} <-> {c2} (Mesafe: {dist:.1f})")
        return patterns
