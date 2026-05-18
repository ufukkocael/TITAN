from agents.companion import CompanionAgent

def test_companion_greeting():
    config = {"name": "TITAN", "personality": "warm"}
    ca = CompanionAgent(config)
    result = ca.respond("Merhaba")
    assert "response" in result

def test_companion_name_learning():
    config = {"name": "TITAN", "personality": "warm"}
    ca = CompanionAgent(config)
    result = ca.respond("adım Ahmet")
    assert "Ahmet" in result["response"]