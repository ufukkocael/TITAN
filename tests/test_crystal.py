import numpy as np
from titan.core.crystal import CrystalLibrary, Crystal, CrystalType, CrystalPurity

def test_create_axiom():
    lib = CrystalLibrary()
    axiom = lib.create_axiom("TestAxiom", np.array([1.0, 0.0, 0.0]), "Test")
    assert axiom.immutable == True
    assert axiom.meltable == False
    assert axiom.purity == CrystalPurity.PURE
    print("✅ Axiom oluşturma")

def test_distill():
    lib = CrystalLibrary()
    crystal = lib.distill(
        name="Memory Leak Fix Pattern",
        vector=np.array([0.8, 0.1, 0.1]),
        source="operator_experience",
        domain="memory_management",
        min_validations=15,
    )
    assert crystal is not None
    assert crystal.type == CrystalType.DISTILLED
    print("✅ Kristal damıtma")

def test_melt():
    lib = CrystalLibrary()
    crystal = lib.distill("Test", np.array([0.5, 0.5, 0.0]), min_validations=10)
    
    original_vector = crystal.vector.copy()
    melted = lib.melt(crystal.id, np.array([0.6, 0.4, 0.0]), success=True)
    
    assert melted is not None
    # Vektör değişmiş olmalı
    diff = np.linalg.norm(original_vector - melted.vector)
    assert diff > 0
    print(f"✅ Kristal eritme (fark: {diff:.4f})")

def test_fuse():
    lib = CrystalLibrary()
    c1 = lib.distill("Pattern A", np.array([1.0, 0.0, 0.0]), min_validations=10)
    c2 = lib.distill("Pattern B", np.array([0.0, 1.0, 0.0]), min_validations=10)
    
    fused = lib.fuse(c1.id, c2.id, "Fused Pattern")
    assert fused is not None
    assert fused.type == CrystalType.FUSED
    print("✅ Kristal birleştirme")

def test_inherit():
    lib = CrystalLibrary()
    source = lib.distill("Source", np.array([0.7, 0.3, 0.0]), min_validations=10)
    
    inherited = lib.inherit(source, new_owner="TITAN-Beta")
    assert inherited.type == CrystalType.INHERITED
    assert inherited.purity_score < source.purity_score
    print("✅ Kristal miras")

def test_immutable_protection():
    lib = CrystalLibrary()
    axiom = lib.create_axiom("Honesty", np.array([1.0, 0.0, 0.0]))
    
    # Değişmez aksiyom eritilemez
    result = lib.melt(axiom.id, np.array([0.5, 0.5, 0.0]), success=True)
    assert result is None
    print("✅ Değişmez aksiyom koruması")

def test_search_by_vector():
    lib = CrystalLibrary()
    lib.distill("Memory", np.array([0.9, 0.1, 0.0]), min_validations=10)
    lib.distill("Security", np.array([0.1, 0.9, 0.0]), min_validations=10)
    
    results = lib.search_by_vector(np.array([0.85, 0.15, 0.0]), top_k=2)
    assert len(results) > 0
    assert "Memory" in results[0][1].name
    print("✅ Vektör araması")

def test_contradictions():
    lib = CrystalLibrary()
    c1 = lib.distill("Safe", np.array([1.0, 1.0, 0.0]), min_validations=10)
    c2 = lib.distill("Risky", np.array([-1.0, -1.0, 0.0]), min_validations=10)
    
    contradictions = lib.find_contradictions(c1)
    assert len(contradictions) > 0
    assert contradictions[0].id == c2.id
    print("✅ Çelişki tespiti")

if __name__ == "__main__":
    test_create_axiom()
    test_distill()
    test_melt()
    test_fuse()
    test_inherit()
    test_immutable_protection()
    test_search_by_vector()
    test_contradictions()
    print("\n🎉 Tüm kristal testleri başarılı!")
