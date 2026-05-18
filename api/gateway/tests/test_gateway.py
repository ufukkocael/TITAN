from middleware.auth import AuthMiddleware
from middleware.circuit_breaker import CircuitBreaker
import asyncio

def test_auth_token():
    auth = AuthMiddleware(secret_key="test", token_expiry=3600)
    token = auth.create_token({"sub": "test"})
    payload = auth.verify_token(token)
    assert payload["sub"] == "test"

def test_circuit_breaker():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    assert cb._get_service_state("test")["state"].value == "closed"