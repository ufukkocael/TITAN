# titan-core/titan/brain/aesthetic_engine.py
import numpy as np
from typing import Dict, List, Tuple

class AestheticEngine:
    """TITAN'ın içsel durumunu görsel sanata ve estetik parametrelere dönüştüren motor."""
    
    def __init__(self):
        self.palettes = {
            "Exuberant": ["#FF007A", "#FFD700", "#00F2FF"], # Enerjik - Pembe, Altın, Camgöbeği
            "Serene": ["#00FF87", "#60EFFF", "#00BFFF"],    # Huzurlu - Yeşil, Turkuaz
            "Agitated": ["#FF4B2B", "#FF416C", "#800000"],  # Huzursuz - Kırmızı, Bordo
            "Melancholic": ["#141E30", "#243B55", "#4B6CB7"], # Melankolik - Lacivert, Koyu Mavi
            "Harmonious": ["#7F00FF", "#E100FF", "#00F2FF"]   # Uyumlu - Mor, Macenta
        }

    def generate_visual_params(self, emotional_state: str, system_load: float, crisis_level: float) -> Dict:
        """Sistemin 'ruh haline' göre görsel parametreler üretir."""
        palette = self.palettes.get(emotional_state, ["#FFFFFF", "#888888"])
        
        return {
            "primary_color": palette[0],
            "accent_color": palette[1],
            "background_glow": palette[2] if len(palette) > 2 else palette[0],
            "particle_density": int(system_load * 100),
            "motion_blur": crisis_level * 0.8,
            "pulse_speed": 1.0 + (crisis_level * 2.0),
            "glitch_intensity": 0.1 if crisis_level < 0.5 else (crisis_level - 0.4)
        }

    def map_tesseract_to_art(self, nodes: List[Dict]) -> Dict:
        """Tesseract düğümlerini sanatsal bir topolojiye dönüştürür."""
        edges = []
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                # Düğümler arası 'bilişsel çekim' varsa bağ kur
                dist = np.linalg.norm(nodes[i]['vector'] - nodes[j]['vector'])
                if dist < 0.5:
                    edges.append({
                        "from": nodes[i]['concept'],
                        "to": nodes[j]['concept'],
                        "opacity": 1.0 - dist,
                        "color": "#00f2ff"
                    })
        
        return {
            "render_mode": "synaptic_network",
            "active_edges": edges,
            "complexity_index": len(edges) / (len(nodes) + 1)
        }
