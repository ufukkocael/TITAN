import pytest
import numpy as np
from titan.core.tesseract import TesseractOrchestrator
from titan.core.compressor import SymbolicCompressor
from titan.core.inertia import InertiaCircle
from titan.core.snapshot import SpiralMemory

def test_tesseract_orchestrator():
    orc = TesseractOrchestrator(dimension=384)
    assert len(orc.nodes) == 5 # Anchors
    
    node = orc.add_node("Test Concept", np.random.randn(384))
    assert node.concept == "Test Concept"
    assert len(orc.nodes) == 6

def test_symbolic_compressor():
    comp = SymbolicCompressor(vector_dim=128)
    vec1 = comp.encode("Apple")
    vec2 = comp.encode("Apple")
    vec3 = comp.encode("Orange")
    
    assert np.allclose(vec1, vec2)
    assert not np.allclose(vec1, vec3)

def test_inertia_circle():
    inertia = InertiaCircle()
    vec = np.array([1.0, 0.0, 0.0])
    alignment = inertia.check_alignment(vec, "HONESTY")
    assert alignment > 0.99

def test_spiral_memory():
    spiral = SpiralMemory(snapshot_size=100)
    node = spiral.add_memory("Memory 1", np.random.randn(384))
    assert node.concept == "Memory 1"
    assert len(spiral.nodes) == 1
