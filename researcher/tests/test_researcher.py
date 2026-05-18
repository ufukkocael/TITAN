from agents.researcher import ResearcherAgent
from learning.distillation import SkillDistillation

def test_formulate_hypothesis():
    r = ResearcherAgent("./test_exp")
    hyp = r.formulate_hypothesis("Sunucu yanıt süreleri arttı")
    assert hyp.question == "Sunucu yanıt süreleri arttı"

def test_skill_distillation():
    sd = SkillDistillation(threshold=0.8)
    new = sd.distill([{"type": "test", "score": 0.95, "context": {}, "pattern": "test"}])
    assert len(new) == 1