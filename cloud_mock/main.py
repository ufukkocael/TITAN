import yaml
import sys
import os
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request
import uvicorn

BASE_DIR = Path(__file__).parent
with open(BASE_DIR / "config.yaml") as f:
    config = yaml.safe_load(f)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 TITAN Cloud Mock Service started")
    try:
        yield
    finally:
        print("🛑 TITAN Cloud Mock Service stopping")

app = FastAPI(title="TITAN Cloud Mock Service", lifespan=lifespan)

BLUEPRINTS = []

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "titan-cloud-mock",
    }

@app.get("/api/v1/vaccines")
async def get_vaccines(env: str = "all", limit: int = 20):
    sample_vector = [0.0] * 384
    vaccines = [
        {
            "symptom_signature": "mock_memory_leak",
            "solution": "apply_memory_hardening_patch",
            "platform": env or "generic",
            "w_score": 0.75,
            "anonymized_vector": sample_vector,
        },
        {
            "symptom_signature": "mock_security_breach",
            "solution": "apply_firewall_hardening",
            "platform": env or "generic",
            "w_score": 0.82,
            "anonymized_vector": sample_vector,
        },
    ]
    return vaccines[:min(limit, len(vaccines))]

@app.post("/api/v1/blueprint")
async def post_blueprint(request: Request):
    payload = await request.json()
    blueprint_id = payload.get("blueprint_id") or f"bp_mock_{len(BLUEPRINTS) + 1}"
    BLUEPRINTS.append({"id": blueprint_id, "payload": payload, "received_at": datetime.utcnow().isoformat() + "Z"})
    return {"status": "created", "blueprint_id": blueprint_id}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config["server"]["host"],
        port=config["server"]["port"],
        reload=True,
    )