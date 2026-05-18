from agents.coder import CoderAgent
from agents.critic import CriticAgent
from tools.patch_generator import PatchGenerator

def test_coder_diagnose():
    coder = CoderAgent()
    result = coder.analyze_error("FATAL: memory leak detected")
    assert result["type"] == "memory_leak"

def test_critic_review():
    critic = CriticAgent()
    result = critic.review("import os\nos.system('rm -rf /')")
    assert not result["approved"]

def test_patch_generator():
    pg = PatchGenerator()
    ptype = pg.diagnose("null pointer exception")
    assert ptype == "null_pointer"