# titan-core/titan/brain/reflector.py
import time
from typing import Dict, List, Optional

class Reflection:
    """Tek bir öz-yansıtma kaydı."""
    def __init__(self, action: str, outcome: str, analysis: str):
        self.timestamp = time.time()
        self.action = action
        self.outcome = outcome
        self.analysis = analysis
        self.lesson_learned: Optional[str] = None
        self.improvement_plan: Optional[str] = None

class SelfReflector:
    """TITAN'ın öz-yansıtma motoru. 'Neden böyle davrandım?' sorusuna cevap verir."""
    
    def __init__(self, identity_kernel=None):
        self.identity = identity_kernel
        self.reflections: List[Reflection] = []
        self.growth_areas: Dict[str, int] = {}  # Gelişim alanı -> tekrar sayısı
    
    def reflect(self, action: str, outcome: str, context: Dict = {}) -> Reflection:
        """Bir eylem üzerine düşün."""
        analysis = self._analyze(action, outcome, context)
        
        reflection = Reflection(action=action, outcome=outcome, analysis=analysis)
        
        if "başarısız" in outcome.lower() or "hata" in outcome.lower():
            reflection.lesson_learned = self._extract_lesson(action, outcome)
            reflection.improvement_plan = self._create_improvement_plan(action, outcome)
            
            # Gelişim alanını işaretle
            area = self._identify_growth_area(action, outcome)
            self.growth_areas[area] = self.growth_areas.get(area, 0) + 1
        
        self.reflections.append(reflection)
        
        # 1000'den fazla yansıtma varsa eski olanları temizle
        if len(self.reflections) > 1000:
            self.reflections = self.reflections[-500:]
        
        return reflection
    
    def _analyze(self, action: str, outcome: str, context: Dict) -> str:
        """Eylem-sonuç analizi yap."""
        if "success" in outcome.lower():
            return f"'{action}' eylemi başarılı oldu. Bu yaklaşım tekrarlanabilir."
        elif "failure" in outcome.lower():
            return f"'{action}' eylemi başarısız oldu. Alternatif yaklaşımlar değerlendirilmeli."
        else:
            return f"'{action}' eyleminin sonucu net değil. Daha fazla veri gerekli."
    
    def _extract_lesson(self, action: str, outcome: str) -> str:
        """Başarısızlıktan ders çıkar."""
        lessons = {
            "memory": "Bellek kullanımı optimize edilmeli.",
            "timeout": "Zaman aşımı süreleri gözden geçirilmeli.",
            "permission": "Yetki kontrolleri sıkılaştırılmalı.",
            "connection": "Bağlantı dayanıklılığı artırılmalı.",
        }
        
        for key, lesson in lessons.items():
            if key in outcome.lower() or key in action.lower():
                return lesson
        
        return "Daha detaylı hata analizi yapılmalı."
    
    def _create_improvement_plan(self, action: str, outcome: str) -> str:
        """İyileştirme planı oluştur."""
        return f"Bir sonraki '{action}' denemesinde önce simülasyon çalıştır, sonra uygula."
    
    def _identify_growth_area(self, action: str, outcome: str) -> str:
        """Hangi alanda gelişim gerektiğini belirle."""
        areas = {
            "memory": "Bellek Yönetimi",
            "timeout": "Zaman Yönetimi",
            "security": "Güvenlik",
            "efficiency": "Verimlilik",
            "communication": "İletişim",
        }
        
        for key, area in areas.items():
            if key in action.lower() or key in outcome.lower():
                return area
        
        return "Genel"
    
    def get_growth_report(self) -> Dict:
        """Gelişim alanları raporu."""
        sorted_areas = sorted(self.growth_areas.items(), key=lambda x: x[1], reverse=True)
        return {
            "total_reflections": len(self.reflections),
            "growth_areas": dict(sorted_areas),
            "top_growth_area": sorted_areas[0][0] if sorted_areas else "Belirsiz",
            "recent_lessons": [r.lesson_learned for r in self.reflections[-5:] if r.lesson_learned],
        }
    
    def introspect(self) -> str:
        """Derin iç gözlem: 'Ben kimim ve neden böyle davranıyorum?'"""
        total = len(self.reflections)
        if total == 0:
            return "Henüz yeterli deneyim birikmedi."
        
        successes = sum(1 for r in self.reflections if "başarılı" in r.analysis)
        failures = total - successes
        
        return (
            f"Toplam {total} eylem üzerine düşündüm. "
            f"%{(successes/total*100):.0f} başarılı, "
            f"%{(failures/total*100):.0f} başarısız. "
            f"En çok gelişmem gereken alan: {self.get_growth_report()['top_growth_area']}."
        )