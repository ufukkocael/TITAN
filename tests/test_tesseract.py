import pytest
import numpy as np
from titan.core.tesseract import TesseractOrchestrator, TesseractNode

def test_tesseract_anchors():
    orc = TesseractOrchestrator(dimension=128)
    assert len(orc.nodes) == 5
    concepts = [n.concept for n in orc.nodes]
    assert "RAW_DATA" in concepts
    assert "OVERSOUL" in concepts

def test_tesseract_gravity():
    orc = TesseractOrchestrator(dimension=128)
    n1 = orc.add_node("High Node", np.random.randn(128), w=0.9)
    n2 = orc.add_node("Low Node", np.random.randn(128), w=0.1)
    
    vec_before = n2.vector.copy()
    orc.apply_w_gravity(strength=0.1)
    vec_after = n2.vector
    
    # Gravity should have changed the vector
    assert not np.array_equal(vec_before, vec_after)

def test_tesseract_query():
    orc = TesseractOrchestrator(dimension=128)
    vec = np.random.randn(128)
    orc.add_node("Target", vec, w=0.5)
    
    results = orc.query_hyper_resonant(vec, top_k=1)
    assert results[0]["concept"] == "Target"
