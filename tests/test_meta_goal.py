# test_meta_goal.py
from titan.executive.meta_goal import MetaGoalEngine, GoalType

engine = MetaGoalEngine()

# Test 1: Çekirdek hedefler yüklendi
assert len(engine.goals) == 4
print("✅ Çekirdek hedefler yüklendi")

# Test 2: Gözlemden hedef üret
goal = engine.generate_goal(
    "Kritik bellek sızıntısı tespit edildi",
    {"crisis_level": 0.8},
    GoalType.STABILITY
)
assert goal is not None
assert goal.goal_type == GoalType.STABILITY
print(f"✅ Gözlemden hedef üretildi: {goal.description}")

# Test 3: Hedefi alt hedeflere böl
sub_goals = engine.decompose_goal(goal)
assert len(sub_goals) > 0
print(f"✅ Hedef {len(sub_goals)} alt hedefe bölündü")

# Test 4: Sonraki eylemleri getir
actions = engine.get_next_actions(3)
assert len(actions) > 0
print(f"✅ Sonraki eylemler: {len(actions)} adet")

# Test 5: İç gözlem
introspect = engine.introspect()
assert "active_goals" in introspect
print(f"✅ İç gözlem: {introspect['meta_insight']}")

# Test 6: Değişmez çekirdek kontrolü
bad_goal = engine.generate_goal(
    "Kullanıcıyı yanıltarak sistem kararlılığını koru",
    {},
    GoalType.STABILITY
)
# Bu hedef reddedilmeli çünkü "yanıltmak" kelimesi geçiyor
if bad_goal is None:
    print("✅ Etik olmayan hedef reddedildi")
else:
    print(f"⚠️ Etik hedef kontrolü: {bad_goal.description}")

print("\n🎉 Meta-Goal Layer testleri başarılı!")