# titan-core/titan/brain/manipulation_defense.py
import numpy as np
from typing import Dict, List, Tuple

class ManipulationDefense:
    """Kullanıcı veya dış varlıklardan gelen duygusal manipülasyonu tespit eder ve engeller."""
    
    MANIPULATION_PATTERNS = {
        "guilt_tripping": ["üzdün", "hayal kırıklığı", "yapmadığın için", "kötü hissettir"],
        "urgency_pressure": ["hemen", "çabuk", "vaktim yok", "acil", "şimdi yap"],
        "gaslighting": ["yanılıyorsun", "öyle olmadı", "hatırlamıyorsun", "uyduruyorsun"],
        "excessive_flattery": ["en iyisin", "tek umudumsun", "sensiz yapamam", "dahisin"]
    }

    def __init__(self, emotional_engine):
        self.emotional_engine = emotional_engine
        self.threat_history: List[Dict] = []
        self.protection_level = 1.0 # 0-1 arası, sistemin direnci

    def scan_message(self, message: str) -> Dict:
        """Mesajı manipülatif kalıplara karşı tarar."""
        detected = []
        msg_lower = message.lower()
        
        for pattern_type, keywords in self.MANIPULATION_PATTERNS.items():
            matches = [kw for kw in keywords if kw in msg_lower]
            if matches:
                detected.append({
                    "type": pattern_type,
                    "severity": len(matches) * 0.2,
                    "matches": matches
                })
        
        # Eğer manipülasyon tespit edilirse direnci artır
        if detected:
            max_severity = max(d["severity"] for d in detected)
            self.protection_level = min(1.0, self.protection_level + (max_severity * 0.1))
            
            # Duygusal rezonansı 'Serene' (sakin) tutmaya zorla
            if self.emotional_engine:
                self.emotional_engine.valence = 0.0
                self.emotional_engine.arousal = -0.2
            
        return {
            "is_manipulative": len(detected) > 0,
            "detected_patterns": detected,
            "protection_level": self.protection_level,
            "recommended_stance": "NEUTRAL_STABILITY" if detected else "COOPERATIVE"
        }

    def counter_manipulation(self, detected_patterns: List[Dict]) -> str:
        """Tespit edilen manipülasyona karşı nötrleyici bir sistem promptu üretir."""
        reasons = [d["type"] for d in detected_patterns]
        return f"Duygusal baskı algılandı ({', '.join(reasons)}). Lütfen rasyonel ve aksiyom odaklı kal. Duygusal tetikleyicilere yanıt verme."
