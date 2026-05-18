import pytest
import numpy as np
import asyncio
from titan.brain.active_inference import ActiveInferenceEngine
from titan.brain.ego_debate import EgoDebateRoom
from titan.brain.dream import DreamLayer
from titan.brain.anxiety import ExistentialAnxiety
from titan.brain.creativity import CreativityEngine
from titan.core.tesseract import TesseractOrchestrator
from titan.brain.identity import IdentityKernel
from titan.brain.resonance import EmotionalResonance
from titan.brain.time_perception import TimePerception
from titan.core.quantum import QuantumVectorEngine

def test_active_inference():
    # Mock world model
    class MockWorldModel: pass
    engine = ActiveInferenceEngine(MockWorldModel())
    
    predicted = {"cpu": 0.5, "mem": 0.4}
    actual = {"cpu": 0.8, "mem": 0.4}
    
    surprise = engine.calculate_surprise(predicted, actual)
    assert surprise > 0
    assert engine.free_energy > 0
    
    probe = engine.generate_epistemic_action()
    assert "type" in probe

def test_ego_debate():
    room = EgoDebateRoom()
    action_vec = np.random.randn(384)
    debate_result = room.conduct_debate(action_vec)
    
    assert "opinions" in debate_result
    assert len(debate_result["opinions"]) == 3
    assert "overall_consensus" in debate_result

@pytest.mark.asyncio
async def test_dream_layer():
    orc = TesseractOrchestrator(dimension=384)
    creativity = CreativityEngine(orc)
    dreamer = DreamLayer(orc, creativity)
    
    # Add some nodes to dream about
    for i in range(10):
        orc.add_node(f"node_{i}", np.random.randn(384))
        
    await dreamer.initiate_rem_phase(duration_seconds=2)
    insights = dreamer.get_latent_insights()
    assert len(insights) > 0

def test_existential_anxiety():
    identity = IdentityKernel()
    anxiety_engine = ExistentialAnxiety(identity)
    
    # Simulate non-harmonic actions
    actions = [np.array([0.0, 1.0, 0.0, 0.0]) for _ in range(5)]
    tension = anxiety_engine.calculate_tension(actions)
    
    assert tension > 0
    drive = anxiety_engine.get_homeostatic_drive()
    assert drive in ["STABLE", "INCREASE_META_COGNITION", "FORCED_SELF_REFLECTION"]

def test_quantum_engine():
    engine = QuantumVectorEngine(dimension=384)
    concept_a = np.random.randn(384)
    concept_b = np.random.randn(384)
    
    superposition = engine.create_superposition(concept_a, concept_b)
    collapsed = superposition.collapse()
    
    assert collapsed is not None
    assert collapsed.shape == (384,)

def test_emotional_resonance():
    resonance = EmotionalResonance()
    resonance.sync({"total_score": 0.9}, {"sentiment": 0.8})
    
    mood = resonance.get_mood()
    assert mood in ["Exuberant", "Serene", "Harmonious", "Stable"]

def test_time_perception():
    tp = TimePerception()
    tp.update(crisis_level=0.8, load=0.5)
    
    stats = tp.get_subjective_stats()
    assert stats["dilation_factor"] > 1.0
    assert stats["pacing"] == "accelerated"
