# titan-core/titan/integration/orchestrator.py (düzeltilmiş importlar)
import asyncio
import time
import json
import numpy as np
from typing import Dict, Optional, List, Any
from datetime import datetime
from enum import Enum

from .bus import MessageBus, Message, EventType
from ..executive.cognitive_scheduler import CognitiveScheduler
from ..executive.priority_manager import CognitiveTask, Priority, PriorityManager
from ..executive.attention_router import AttentionRouter, AttentionFocus
from ..executive.resource_allocator import ResourceAllocator
from ..executive.meta_goal import MetaGoalEngine, GoalType, GoalStatus, Goal
from ..brain.world_model import InternalSimulator
from ..brain.evaluator import HonestyEvaluator
from ..brain.identity import IdentityKernel
from ..brain.reasoning import ReasoningEngine
from ..brain.reflector import SelfReflector
from ..brain.meta_cognition import MetaCognitionController
from ..brain.social_model import SocialBrain
from ..brain.creativity import CreativityEngine
from ..brain.dream import DreamLayer
from ..brain.anxiety import ExistentialAnxiety
from ..brain.imagery import MentalCanvas
from ..brain.time_perception import TimePerception
from ..brain.resonance import EmotionalResonance
from ..brain.aesthetic_engine import AestheticEngine
from ..brain.evolution import CodeEvolver
from ..brain.entropy import NeuralEntropyManager
from ..brain.multilingual import MultilingualSynthesis
from ..brain.manipulation_defense import ManipulationDefense
from ..stability.antifragility import AntifragilityEngine
from ..brain.collective import CollectiveSubconscious
from ..brain.ethics_simulator import EthicalDilemmaSimulator
from ..brain.self_education import SelfEducationEngine
from ..brain.active_inference import ActiveInferenceEngine
from ..brain.ego_debate import EgoDebateRoom
from ..core.quantum import QuantumVectorEngine
from ..tools.llm import LLMGateway
from ..memory.vault import WisdomVault
from ..memory.episodic import EpisodicMemory
from ..memory.semantic import SemanticMemory
from ..memory.working import WorkingMemory
from ..core.tesseract import TesseractOrchestrator
from ..core.inertia import InertiaCircle
from ..core.crystal import CrystalLibrary, CrystalType
from ..core.maestro import Maestro
from ..predictive import PredictiveEngine
from ..security import SafetyGate, ActionLevel
from ..tools.cloud import WisdomExchangeClient


class SystemMode(Enum):
    INITIALIZING = "initializing"
    NORMAL = "normal"
    CRISIS = "crisis"
    LEARNING = "learning"
    EXPLORING = "exploring"
    MAINTENANCE = "maintenance"
    SHUTTING_DOWN = "shutting_down"


class TitanOrchestrator:
    """TITAN V4'ün ana orkestratörü."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # === TEMEL BİLEŞENLER ===
        self.bus = MessageBus()
        self.tesseract = TesseractOrchestrator(dimension=384)
        self.inertia = InertiaCircle()
        self.crystal_lib = CrystalLibrary()
        
        # === BELLEK SİSTEMLERİ ===
        self.vault = WisdomVault(path=self.config.get("memory_path", "./titan_memory"))
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.working = WorkingMemory()
        
        # === BEYİN SİSTEMLERİ ===
        self.identity = IdentityKernel()
        self.evaluator = HonestyEvaluator(self.identity, self.crystal_lib)
        self.reasoning = ReasoningEngine(evaluator=self.evaluator)
        self.reflector = SelfReflector(self.identity)
        self.meta_cognition = MetaCognitionController()
        self.social_mind = SocialBrain()
        self.creativity = CreativityEngine(self.tesseract)
        self.dream_layer = DreamLayer(self.tesseract, self.creativity)
        self.anxiety_engine = ExistentialAnxiety(self.identity)
        self.time_engine = TimePerception()
        self.emotional_engine = EmotionalResonance()
        self.aesthetic_engine = AestheticEngine()
        
        # LLM Gateway (config'ten al)
        llm_config = self.config.get("llm", {"provider": "ollama", "ollama_model": "llama3.2:3b"})
        self.llm_gateway = LLMGateway(llm_config)
        
        self.code_evolver = CodeEvolver(self.llm_gateway)
        self.multilingual = MultilingualSynthesis(self.llm_gateway)
        self.manipulation_defense = ManipulationDefense(self.emotional_engine)
        
        # Cloud ve Kolektif
        self.exchange = WisdomExchangeClient(
            local_vault=self.vault,
            central_url=self.config.get("central_url", "http://localhost:9100"),
            fallback_urls=self.config.get("fallback_urls", [])
        )
        self.collective_mind = CollectiveSubconscious(self.exchange, self.dream_layer)
        self.ethics_simulator = EthicalDilemmaSimulator(self.evaluator)
        self.simulator = InternalSimulator()
        self.active_inference = ActiveInferenceEngine(self.simulator)
        self.ego_room = EgoDebateRoom()
        self.entropy_manager = NeuralEntropyManager(self.tesseract)
        self.maestro = Maestro(self)
        
        # Antifragility Engine (import hatası düzeltildi)
        try:
            self.antifragility = AntifragilityEngine(self.code_evolver, self.crystal_lib, self.config.get("stability"))
        except Exception as e:
            print(f"⚠️ Antifragility Engine yüklenemedi: {e}")
            self.antifragility = None
        
        self.meta_goal = MetaGoalEngine(identity_kernel=self.identity)
        self.education = SelfEducationEngine(self.llm_gateway, self.meta_goal, self.semantic)
        self.quantum_engine = QuantumVectorEngine(dimension=384)
        self.imagery_canvas = MentalCanvas(resolution=64)
        self.predictive = PredictiveEngine()
        
        # === YÖNETİM SİSTEMLERİ ===
        self.scheduler = CognitiveScheduler()
        self.attention = AttentionRouter()
        self.resources = ResourceAllocator()
        self.safety = SafetyGate()
        
        # === DURUM ===
        self.mode = SystemMode.INITIALIZING
        self.system_state = {
            "status": "initializing",
            "crisis_level": 0.0,
            "uptime": 0.0,
            "start_time": time.time(),
            "total_events_processed": 0,
            "total_tasks_completed": 0,
            "total_goals_achieved": 0,
            "current_focus": "initialization",
        }
        
        # === MOD BAĞLANTILARI ===
        self.connected_mods: Dict[str, bool] = {
            "operator": False,
            "programmer": False,
            "researcher": False,
            "companion": False,
        }
        
        # === ÇEKİRDEK AKSİYOMLAR ===
        self._init_crystal_axioms()
        
        # === İSTATİSTİKLER ===
        self.stats = {
            "events_by_type": {},
            "tasks_by_source": {},
            "decisions_made": 0,
            "crisis_resolved": 0,
            "patches_generated": 0,
            "hypotheses_tested": 0,
        }
        
        # === ÇALIŞMA DURUMU ===
        self.running = False
        self._background_tasks: List[asyncio.Task] = []
        
        # === OLAY İŞLEYİCİLER ===
        self._register_all_handlers()
    
    def _init_crystal_axioms(self):
        """Sistemin değişmez kristalize kurallarını tanımlar."""
        self.crystal_lib.create_axiom(
            "GeometricHonesty", 
            np.array([1.0, 0.0, 0.0, 0.0]), 
            "Harmonik dürüstlük"
        )
        self.crystal_lib.create_axiom(
            "SystemIntegrity", 
            np.array([0.0, 1.0, 0.0, 0.0]), 
            "Sistem bütünlüğü"
        )
        self.crystal_lib.create_axiom(
            "HumanService", 
            np.array([0.0, 0.0, 1.0, 0.0]), 
            "İnsana hizmet"
        )
        self.crystal_lib.create_axiom(
            "SelfEvolution", 
            np.array([0.0, 0.0, 0.0, 1.0]), 
            "Öz-evrim"
        )
    
    def _register_all_handlers(self):
        """Tüm olay işleyicilerini kaydet."""
        # Basit handler'lar
        self.bus.subscribe_all(self._log_event)
    
    async def _log_event(self, msg: Message):
        """Tüm olayları logla."""
        self.system_state["total_events_processed"] += 1
    
    async def start(self):
        """Orchestrator'ı başlat."""
        self.running = True
        self.mode = SystemMode.NORMAL
        self.system_state["status"] = "running"
        print("✅ TITAN V4 Orchestrator başlatıldı.")
    
    async def shutdown(self):
        """Orchestrator'ı kapat."""
        self.running = False
        self.mode = SystemMode.SHUTTING_DOWN
        print("🛑 TITAN V4 Orchestrator kapatılıyor.")
    
    def connect_mod(self, mod_name: str):
        """Bir modun bağlandığını bildir."""
        if mod_name in self.connected_mods:
            self.connected_mods[mod_name] = True
            print(f"🔗 {mod_name} modu bağlandı.")
    
    def disconnect_mod(self, mod_name: str):
        """Bir modun bağlantısının koptuğunu bildir."""
        if mod_name in self.connected_mods:
            self.connected_mods[mod_name] = False
            print(f"🔌 {mod_name} modu bağlantısı koptu.")
    
    async def process_event(self, event: Dict) -> Dict:
        """Dışarıdan gelen bir olayı işle."""
        msg = Message(
            id=f"ext_{int(time.time())}",
            type=EventType.USER_REQUEST,
            source=event.get("source", "external"),
            target=event.get("target"),
            payload=event.get("payload", {}),
        )
        await self.bus.publish(msg)
        return {"status": "processed", "event_id": msg.id}
    
    def get_system_report(self) -> Dict:
        """Sistem durum raporu."""
        return {
            "orchestrator": {
                "mode": self.mode.value,
                "status": self.system_state["status"],
                "uptime_seconds": time.time() - self.system_state["start_time"],
                "crisis_level": self.system_state["crisis_level"],
            },
            "mods": self.connected_mods,
            "stats": self.stats,
        }
    
    def get_quick_status(self) -> str:
        """Hızlı durum özeti."""
        return f"TITAN V4 [{self.mode.value}] | Kriz: {self.system_state['crisis_level']:.1%} | Modlar: {sum(self.connected_mods.values())}/4"