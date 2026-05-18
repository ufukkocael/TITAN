import pytest
import numpy as np
from titan.brain.identity import IdentityKernel
from titan.brain.evaluator import HonestyEvaluator
from titan.brain.reasoning import ReasoningEngine
from titan.brain.reflector import SelfReflector
from titan.brain.world_model import InternalSimulator

def test_identity_kernel():
    id_kernel = IdentityKernel()
    weights = id_kernel.get_weights()
    assert weights["HONESTY"] == 0.6

def test_honesty_evaluator():
    evaluator = HonestyEvaluator()
    vec = np.random.randn(384)
    result = evaluator.evaluate(vec)
    assert "total_score" in result

def test_reasoning_engine():
    engine = ReasoningEngine()
    chain = engine.chain_of_thought("Why is the system slow?")
    assert len(chain) > 0

def test_self_reflector():
    reflector = SelfReflector()
    reflection = reflector.reflect("Action A", "Success")
    assert reflection.action == "Action A"

def test_world_model():
    sim = InternalSimulator()
    possible = {"cpu": [0.1, 0.5, 0.9]}
    outcomes = sim.predict_outcomes("test", {}, possible)
    assert len(outcomes) > 0
