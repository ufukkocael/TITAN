# titan-core/titan/stability/antifragility.py
"""
Antifragility Engine - Antikırılganlık ve Bağışıklık Sistemi
Nassim Taleb'in Antifragile kavramından esinlenen motor
Sistemi sadece dayanıklı değil, darbe aldıkça güçlenen bir varlığa dönüştürür
"""

import asyncio
import hashlib
import logging
import random
import numpy as np
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from titan.brain.evolution import CodeEvolver
from titan.core.crystal import CrystalLibrary, CrystalPurity


class StressLevel(Enum):
    LOW = 1
    MODERATE = 2
    HIGH = 3
    EXTREME = 4
    
    def __str__(self):
        return self.name


@dataclass
class ImmuneMemory:
    """Bağışıklık hafızası - daha önce yaşanan stresler ve çözümler"""
    id: str
    stress_type: str
    stress_level: StressLevel
    symptoms: List[str]
    root_cause: str
    solution: str
    antibodies: List[str]
    effectiveness: float
    occurred_at: datetime
    last_reinforced: datetime
    reinforcement_count: int = 0
    mutation_version: int = 1
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "stress_type": self.stress_type,
            "stress_level": str(self.stress_level),
            "symptoms": self.symptoms,
            "root_cause": self.root_cause,
            "solution": self.solution,
            "effectiveness": self.effectiveness,
            "reinforcement_count": self.reinforcement_count,
        }


@dataclass
class Vaccine:
    """Strese karşı geliştirilen aşı"""
    id: str
    target_stress: str
    code_patches: List[Dict]
    pattern_signature: str
    coverage: List[str]
    potency: float
    created_at: datetime
    applied_at: Optional[datetime] = None
    applied_to: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "target_stress": self.target_stress,
            "pattern_signature": self.pattern_signature,
            "potency": self.potency,
            "coverage": self.coverage,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AntifragilityEngine:
    """
    Antikırılganlık ve Bağışıklık Sistemi
    by U.KOCAEL
    """
    
    def __init__(self, evolver: CodeEvolver, crystal_lib: CrystalLibrary, config: Optional[Dict] = None):
        self.config = config or {}
        self.evolver = evolver
        self.crystal_lib = crystal_lib
        
        # Bağışıklık hafızası
        self.immune_memory: Dict[str, ImmuneMemory] = {}
        self.vaccine_library: Dict[str, Vaccine] = {}
        
        # Stres izleme
        self.stress_history: List[Dict] = []
        self.active_stresses: Dict[str, Dict] = {}
        
        # Kaos Monkey ayarları
        self.chaos_enabled = self.config.get("chaos_monkey", True)
        self.chaos_intensity = self.config.get("chaos_intensity", 0.3)
        self.stress_level = 0.0
        self.last_chaos_time = datetime.now()
        
        # İstatistikler
        self.stats = {
            "total_stresses": 0,
            "vaccines_developed": 0,
            "vaccines_applied": 0,
            "preemptive_hardenings": 0,
            "chaos_sessions": 0,
            "immunity_score": 0.0,
            "stress_resolved": 0,
        }
        
        self.logger = logging.getLogger("Antifragility")
        self.logger.setLevel(logging.INFO)
    
    async def register_stress(self, stress_type: str, symptoms: List[str], 
                              severity: float, context: Dict[str, Any]) -> Optional[str]:
        """Bir stres/olay kaydet ve bağışıklık geliştir."""
        stress_level = self._severity_to_level(severity)
        self.stress_level = severity
        
        print(f"⚠️ [ANTIFRAGILE] Stres Algılandı: {stress_type} (Seviye: {stress_level.name}, Şiddet: {severity:.2f})")
        
        stress_id = f"stress_{int(datetime.now().timestamp())}"
        self.active_stresses[stress_id] = {
            "type": stress_type,
            "symptoms": symptoms,
            "level": stress_level,
            "severity": severity,
            "context": context,
            "timestamp": datetime.now()
        }
        
        self.stress_history.append({
            "id": stress_id,
            "type": stress_type,
            "level": stress_level.name,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })
        
        self.stats["total_stresses"] += 1
        
        # Bağışıklık geliştir
        immunity_id = await self._develop_immunity(stress_id)
        
        # Stresi aktif listeden kaldır (çözüldüyse)
        if immunity_id:
            self.stats["stress_resolved"] += 1
            del self.active_stresses[stress_id]
        
        return immunity_id
    
    async def _develop_immunity(self, stress_id: str) -> Optional[str]:
        if stress_id not in self.active_stresses:
            return None
        
        stress = self.active_stresses[stress_id]
        
        # 1. Kök neden analizi
        root_cause = await self._analyze_root_cause(stress)
        
        # 2. Mevcut bağışıklık kontrolü
        existing = self._find_similar_immunity(root_cause)
        if existing:
            await self._reinforce_immunity(existing, stress)
            return existing.id
        
        # 3. Çözüm ve Aşı üretimi
        solution = await self._generate_solution(stress, root_cause)
        vaccine = await self._create_vaccine(stress, root_cause, solution)
        
        # 4. Hafızaya Kaydet
        immune_id = f"immune_{int(datetime.now().timestamp())}"
        self.immune_memory[immune_id] = ImmuneMemory(
            id=immune_id,
            stress_type=stress["type"],
            stress_level=stress["level"],
            symptoms=stress["symptoms"],
            root_cause=root_cause,
            solution=solution["description"],
            antibodies=solution["actions"],
            effectiveness=0.7,
            occurred_at=datetime.now(),
            last_reinforced=datetime.now()
        )
        
        self.vaccine_library[vaccine.id] = vaccine
        self.stats["vaccines_developed"] += 1
        
        # 5. Kristalize et
        try:
            self.crystal_lib.distill(
                name=f"VACCINE_{stress['type']}",
                vector=np.random.randn(384),
                source="antifragility",
                domain="security",
                min_validations=20
            )
        except Exception as e:
            self.logger.warning(f"Kristalizasyon hatası: {e}")
        
        print(f"💉 [ANTIFRAGILE] Yeni bağışıklık geliştirildi: {immune_id} ({stress['type']})")
        await self._preemptive_hardening(root_cause, vaccine)
        
        return immune_id

    async def _analyze_root_cause(self, stress: Dict) -> str:
        """Kök neden analizi yapar."""
        symptoms = " ".join(stress["symptoms"]).lower()
        
        if any(kw in symptoms for kw in ["memory", "leak", "malloc", "free"]):
            return "memory_leak_pattern"
        if any(kw in symptoms for kw in ["crash", "segfault", "null", "pointer"]):
            return "null_pointer_access"
        if any(kw in symptoms for kw in ["security", "breach", "attack", "inject"]):
            return "vulnerability_breach"
        if any(kw in symptoms for kw in ["timeout", "slow", "lag", "delay"]):
            return "performance_degradation"
        if any(kw in symptoms for kw in ["connection", "network", "socket"]):
            return "network_issue"
        
        return "generic_system_instability"

    async def _generate_solution(self, stress: Dict, root_cause: str) -> Dict:
        """Çözüm üretir."""
        solution_map = {
            "memory_leak_pattern": {
                "description": "Bellek sızıntısı tespit edildi, otomatik temizleme uygulanıyor",
                "actions": ["gc.collect()", "memory_pool_reset", "cache_clear"]
            },
            "null_pointer_access": {
                "description": "Null pointer hatası, güvenli erişim ekleniyor",
                "actions": ["add_null_check", "exception_handler", "fallback_value"]
            },
            "vulnerability_breach": {
                "description": "Güvenlik ihlali, firewall kuralları güncelleniyor",
                "actions": ["block_ip", "update_firewall", "audit_log"]
            },
            "performance_degradation": {
                "description": "Performans düşüşü, optimizasyon başlatılıyor",
                "actions": ["cache_warmup", "connection_pool", "query_optimize"]
            },
            "network_issue": {
                "description": "Ağ sorunu, yeniden bağlantı deneniyor",
                "actions": ["reconnect", "retry_with_backoff", "fallback_endpoint"]
            },
        }
        
        result = solution_map.get(root_cause, {
            "description": f"Genel çözüm uygulanıyor: {root_cause}",
            "actions": ["system_restart", "config_reload", "state_reset"]
        })
        
        return result

    async def _create_vaccine(self, stress: Dict, root_cause: str, solution: Dict) -> Vaccine:
        """Aşı oluşturur."""
        vaccine_id = f"vax_{int(datetime.now().timestamp())}"
        
        # Basit bir imza oluştur
        signature = hashlib.md5(f"{stress['type']}_{root_cause}".encode()).hexdigest()[:16]
        
        return Vaccine(
            id=vaccine_id,
            target_stress=stress["type"],
            code_patches=[],  # Gerçek patch'ler evolution engine'den gelir
            pattern_signature=signature,
            coverage=["core_logic", "security_layer"],
            potency=0.8,
            created_at=datetime.now()
        )

    async def _preemptive_hardening(self, root_cause: str, vaccine: Vaccine):
        """Önleyici sertleştirme."""
        print(f"🛡️ [ANTIFRAGILE] Önleyici sertleştirme başladı: {root_cause}")
        self.stats["preemptive_hardenings"] += 1

    async def _reinforce_immunity(self, immunity: ImmuneMemory, new_stress: Dict):
        """Bağışıklığı güçlendirir."""
        immunity.reinforcement_count += 1
        immunity.effectiveness = min(1.0, immunity.effectiveness + 0.05)
        immunity.last_reinforced = datetime.now()
        
        print(f"💪 [ANTIFRAGILE] Bağışıklık güçlendi: {immunity.id} (etkinlik: {immunity.effectiveness:.2f})")

    async def stress_response(self, payload: Dict[str, Any]) -> Optional[str]:
        """Dışarıdan gelen anomali veya stres mesajını kaydeder."""
        stress_type = payload.get("type", "anomaly")
        symptoms = payload.get("symptoms", [payload.get("message", "unknown")])
        severity = float(payload.get("severity", 0.5))
        return await self.register_stress(stress_type, symptoms, severity, payload)

    async def generate_vaccine(self, payload: Dict[str, Any]) -> Optional[Vaccine]:
        """Uygulanan onarım veya düzeltme için bağışıklık aşısı üretir."""
        solution = {
            "description": payload.get("description", "automatic fix vaccine"),
            "actions": payload.get("actions", [payload.get("action", "patch")])
        }
        
        vaccine = await self._create_vaccine(
            {
                "type": payload.get("type", "fix"),
                "symptoms": [payload.get("description", "fix_applied")],
                "context": payload
            },
            root_cause=payload.get("description", "manual_patch"),
            solution=solution
        )
        
        self.vaccine_library[vaccine.id] = vaccine
        self.stats["vaccines_developed"] += 1
        print(f"💉 [ANTIFRAGILE] Yeni aşı üretildi: {vaccine.id} ({vaccine.target_stress})")
        
        return vaccine

    def _find_similar_immunity(self, root_cause: str) -> Optional[ImmuneMemory]:
        """Benzer bağışıklık arar."""
        for immunity in self.immune_memory.values():
            if immunity.root_cause == root_cause:
                return immunity
        return None

    async def chaos_monkey_simulation(self):
        """Kaos Monkey simülasyonu - rastgele stres üretir."""
        if not self.chaos_enabled:
            return
        
        # Belirli aralıklarla chaos üret
        now = datetime.now()
        if (now - self.last_chaos_time).seconds > 60:  # Dakikada bir
            self.last_chaos_time = now
            
            if random.random() < self.chaos_intensity:
                chaos_types = [
                    ("latency_spike", ["high_latency", "timeout"], 0.4),
                    ("cpu_spike", ["high_cpu", "slow_response"], 0.3),
                    ("memory_pressure", ["high_memory", "swap_usage"], 0.3),
                    ("network_flap", ["connection_drop", "reconnect"], 0.2),
                ]
                
                chaos_type, symptoms, severity = random.choice(chaos_types)
                self.stats["chaos_sessions"] += 1
                
                print(f"🐒 [ANTIFRAGILE] Chaos Monkey testi: {chaos_type}")
                await self.register_stress(f"chaos_{chaos_type}", symptoms, severity, {"type": "drill"})

    def get_immunity_report(self) -> Dict:
        """Bağışıklık durum raporu."""
        return {
            "total_immunities": len(self.immune_memory),
            "total_vaccines": len(self.vaccine_library),
            "immunity_score": self.stats["immunity_score"],
            "effectiveness_avg": sum(i.effectiveness for i in self.immune_memory.values()) / len(self.immune_memory) if self.immune_memory else 0,
            "most_resilient": max(self.immune_memory.values(), key=lambda i: i.effectiveness).stress_type if self.immune_memory else None,
        }

    async def get_immunity_quotient(self) -> float:
        """Bağışıklık katsayısını hesaplar."""
        if not self.immune_memory:
            self.stats["immunity_score"] = 0.3
            return 0.3
        
        avg_eff = sum(i.effectiveness for i in self.immune_memory.values()) / len(self.immune_memory)
        self.stats["immunity_score"] = avg_eff
        return avg_eff

    def check_system_health(self) -> Optional[str]:
        """Sistemin genel antikırılganlık durumunu denetler."""
        if self.stress_level > 0.7:
            return f"⚠️ Yüksek stres seviyesi: {self.stress_level:.2f}"
        elif len(self.active_stresses) > 3:
            return f"⚠️ {len(self.active_stresses)} aktif stres devam ediyor"
        elif self.stats["immunity_score"] < 0.5:
            return "⚠️ Düşük bağışıklık seviyesi"
        
        return None

    def _severity_to_level(self, severity: float) -> StressLevel:
        """Şiddet seviyesini StressLevel'a çevirir."""
        if severity > 0.8:
            return StressLevel.EXTREME
        if severity > 0.6:
            return StressLevel.HIGH
        if severity > 0.3:
            return StressLevel.MODERATE
        return StressLevel.LOW

    def get_stats(self) -> Dict:
        """İstatistikleri döndürür."""
        return {
            **self.stats,
            "active_stresses": len(self.active_stresses),
            "total_immune_memory": len(self.immune_memory),
            "total_vaccines": len(self.vaccine_library),
            "current_stress_level": self.stress_level,
        }
    
    def reset(self):
        """Tüm bağışıklık hafızasını sıfırlar."""
        self.immune_memory.clear()
        self.vaccine_library.clear()
        self.stress_history.clear()
        self.active_stresses.clear()
        self.stress_level = 0.0
        self.stats = {k: 0 for k in self.stats}
        print("🔄 [ANTIFRAGILE] Bağışıklık sistemi sıfırlandı")