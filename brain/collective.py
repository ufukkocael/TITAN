# titan-core/titan/brain/collective.py
import time
from typing import List, Dict, Optional
from ..tools.cloud import WisdomExchangeClient
from .dream import DreamLayer

class CollectiveSubconscious:
    """TITAN üniteleri arasında paylaşılan rüya ve sezgi havuzu."""
    
    def __init__(self, exchange_client: WisdomExchangeClient, dream_layer: DreamLayer):
        self.exchange = exchange_client
        self.dream_layer = dream_layer
        self.shared_archetypes: List[Dict] = []
        self.last_sync = 0
    
    async def broadcast_dream(self):
        """Yerel rüyalardan damıtılmış bir sezgiyi (insight) küresel ağa gönderir."""
        insights = self.dream_layer.get_latent_insights()
        if not insights:
            return
            
        latest_insight = insights[-1]
        print(f"🌌 [COLLECTIVE] Rüya kristalize ediliyor ve Katedral'e gönderiliyor: {latest_insight}")
        
        # Vektörleştirilmiş rüyayı paylaş
        import numpy as np
        await self.exchange.share_wisdom(
            concept=f"dream_{latest_insight}",
            vector=np.random.randn(384), # Rüya vektörü
            metadata={"type": "latent_archetype", "source": "dream_layer"}
        )

    async def absorb_archetypes(self):
        """Küresel ağdan diğer TITAN'ların 'rüyalarını' (arketipler) çeker."""
        vaccines = await self.exchange.fetch_vaccines(environment="latent_space", limit=5)
        for v in vaccines:
            archetype = {
                "id": v.get("blueprint_id"),
                "concept": v.get("symptom_signature"),
                "insight": v.get("solution"),
                "purity": v.get("w_score")
            }
            if archetype not in self.shared_archetypes:
                self.shared_archetypes.append(archetype)
                print(f"🧬 [COLLECTIVE] Yeni bir küresel arketip emildi: {archetype['concept']}")
        
        self.last_sync = time.time()

    def get_collective_guidance(self) -> List[str]:
        """Kolektif bilinçaltından gelen yönlendirmeleri döndürür."""
        return [a["concept"] for a in self.shared_archetypes[-5:]]
