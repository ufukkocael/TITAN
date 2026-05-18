"""
TITAN V4 Brain Module - Bilişsel ve nöral katmanlar
"""

from .reasoning import ReasoningEngine, ReasoningStrategy, ReasoningStep
from .world_model import InternalSimulator, SimulationState
from .predictor import ActionPredictor
from .reflector import SelfReflector, Reflection
from .identity import IdentityKernel
from .evaluator import HonestyEvaluator
from .meta_cognition import MetaCognitionController, CognitiveState
from .social_model import SocialBrain, EntityState
from .creativity import CreativityEngine
from .dream import DreamLayer
from .anxiety import ExistentialAnxiety
from .imagery import MentalCanvas
from .time_perception import TimePerception
from .resonance import EmotionalResonance
from .manipulation_defense import ManipulationDefense
from .multilingual import MultilingualSynthesis
from .evolution import CodeEvolver
from .entropy import NeuralEntropyManager
from .aesthetic_engine import AestheticEngine
from .collective import CollectiveSubconscious
from .ethics_simulator import EthicalDilemmaSimulator, EthicalDilemma
from .self_education import SelfEducationEngine
from .active_inference import ActiveInferenceEngine
from .ego_debate import EgoDebateRoom, InternalEgo

__all__ = [
    "ReasoningEngine", "ReasoningStrategy", "ReasoningStep",
    "InternalSimulator", "SimulationState",
    "ActionPredictor",
    "SelfReflector", "Reflection",
    "IdentityKernel",
    "HonestyEvaluator",
    "MetaCognitionController", "CognitiveState",
    "SocialBrain", "EntityState",
    "CreativityEngine",
    "DreamLayer",
    "ExistentialAnxiety",
    "MentalCanvas",
    "TimePerception",
    "EmotionalResonance",
    "ManipulationDefense",
    "MultilingualSynthesis",
    "CodeEvolver",
    "NeuralEntropyManager",
    "AestheticEngine",
    "CollectiveSubconscious",
    "EthicalDilemmaSimulator", "EthicalDilemma",
    "SelfEducationEngine",
    "ActiveInferenceEngine",
    "EgoDebateRoom", "InternalEgo",
]