# titan-core/titan/memory/semantic.py
from typing import Dict, List, Optional, Tuple
import numpy as np

class SemanticMemory:
    """TITAN'ın kavramsal bilgi belleği. 'Ne biliyorum?' sorusuna cevap verir."""
    
    def __init__(self):
        self.facts: Dict[str, Dict] = {}           # Kavram -> {bilgi}
        self.relationships: List[Tuple[str, str, str]] = []  # (özne, ilişki, nesne)
        self.categories: Dict[str, List[str]] = {} # Kategori -> [kavramlar]
        self.certainty: Dict[str, float] = {}      # Kavram -> kesinlik (0-1)
    
    def learn_fact(self, concept: str, fact: Dict, certainty: float = 0.5):
        """Yeni bir bilgi öğren."""
        if concept not in self.facts:
            self.facts[concept] = {}
        self.facts[concept].update(fact)
        self.certainty[concept] = certainty
    
    def learn_relationship(self, subject: str, relation: str, obj: str):
        """İki kavram arasında ilişki kur."""
        self.relationships.append((subject, relation, obj))
    
    def categorize(self, concept: str, category: str):
        """Bir kavramı kategoriye ekle."""
        if category not in self.categories:
            self.categories[category] = []
        if concept not in self.categories[category]:
            self.categories[category].append(concept)
    
    def query(self, concept: str) -> Optional[Dict]:
        """Bir kavram hakkında bilinenleri getir."""
        return self.facts.get(concept)
    
    def query_related(self, concept: str) -> List[Tuple[str, str, str]]:
        """Bir kavramla ilgili tüm ilişkileri getir."""
        return [(s, r, o) for s, r, o in self.relationships 
                if s == concept or o == concept]
    
    def get_category_members(self, category: str) -> List[str]:
        """Bir kategorideki tüm kavramları getir."""
        return self.categories.get(category, [])
    
    def get_certainty(self, concept: str) -> float:
        """Bir bilginin kesinlik derecesini getir."""
        return self.certainty.get(concept, 0.0)
    
    def reinforce(self, concept: str, amount: float = 0.1):
        """Bir bilgiyi pekiştir (kesinliği artır)."""
        if concept in self.certainty:
            self.certainty[concept] = min(1.0, self.certainty[concept] + amount)
    
    def weaken(self, concept: str, amount: float = 0.1):
        """Bir bilgiyi zayıflat (kesinliği azalt)."""
        if concept in self.certainty:
            self.certainty[concept] = max(0.0, self.certainty[concept] - amount)
    
    def get_stats(self) -> Dict:
        return {
            "total_facts": len(self.facts),
            "total_relationships": len(self.relationships),
            "total_categories": len(self.categories),
            "average_certainty": np.mean(list(self.certainty.values())) if self.certainty else 0.0,
        }