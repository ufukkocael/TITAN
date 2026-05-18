# titan-core/tests/test_core.py
import sys
sys.path.insert(0, '.')
from titan import SymbolicCompressor, SpiralMemory, InertiaCircle
from titan import TesseractOrchestrator, WisdomVault, IdentityKernel, HonestyEvaluator
from titan import SafetyGate, ActionLevel, PredictiveEngine
import numpy as np

# Test 1: Compressor
c = SymbolicCompressor(64)
v1 = c.encode("hello")
v2 = c.encode("hello")
assert np.allclose(v1, v2), "Aynı kavram farklı vektör üretti"
print("✓ Compressor")

# Test 2: Spiral Memory
sm = SpiralMemory(1024)
n = sm.add_memory("test", np.random.randn(64))
assert len(sm.nodes) == 1
print("✓ SpiralMemory")

# Test 3: InertiaCircle
ic = InertiaCircle()
assert "HONESTY" in ic.core_axioms
print("✓ InertiaCircle")

# Test 4: Tesseract
to = TesseractOrchestrator(64)
assert len(to.anchors) == 5
to.add_node("test_log", np.random.randn(64))
assert len(to.nodes) == 6
print("✓ TesseractOrchestrator")

# Test 5: WisdomVault
wv = WisdomVault("./test_vault")
wv.archive("test", np.random.randn(64), {"solution": "restart"})
r = wv.recall(np.random.randn(64))
print("✓ WisdomVault")

# Test 6: Identity + Evaluator
ik = IdentityKernel()
assert ik.PRIMARY_AXIOM["immutable"] == True
he = HonestyEvaluator(ik)
result = he.evaluate(np.array([1.0, 0.5, 0.3]))
assert result["approved"] == True
print("✓ IdentityKernel + HonestyEvaluator")

# Test 7: SafetyGate
assert SafetyGate.classify("delete", "db") == ActionLevel.DANGEROUS
assert SafetyGate.classify("restart", "service") == ActionLevel.CONDITIONAL
assert SafetyGate.classify("read", "log") == ActionLevel.SAFE
print("✓ SafetyGate")

# Test 8: PredictiveEngine
pe = PredictiveEngine(window_seconds=60, threshold=3)
for _ in range(3):
    pe.feed("linux", "CRITICAL", "OOM error")
alert = pe.feed("linux", "CRITICAL", "OOM error")
assert alert is not None and alert["count"] >= 3
print("✓ PredictiveEngine")

print("\n🎉 Tüm testler başarılı! titan-core hazır.")