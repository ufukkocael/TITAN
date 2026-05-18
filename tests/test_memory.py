import pytest
import numpy as np
from titan.memory.vault import WisdomVault
from titan.memory.episodic import EpisodicMemory
from titan.memory.semantic import SemanticMemory
from titan.memory.working import WorkingMemory

def test_wisdom_vault(tmp_path):
    vault = WisdomVault(path=str(tmp_path))
    vec = np.random.randn(384)
    vault.archive("Concept A", vec, {"meta": "data"})
    result = vault.recall(vec)
    assert len(result["documents"]) > 0

def test_episodic_memory():
    mem = EpisodicMemory()
    mem.record("System crash", {"crisis": 0.8}, "failure")
    assert len(mem.episodes) == 1
    assert mem.milestones[0].event == "System crash"

def test_semantic_memory():
    mem = SemanticMemory()
    mem.learn_fact("Python", {"type": "language"})
    assert mem.query("Python")["type"] == "language"

def test_working_memory():
    mem = WorkingMemory(capacity=5)
    mem.hold("Thought 1", "T1")
    assert mem.get_by_label("T1")["item"] == "Thought 1"
