# services/researcher/main.py
import asyncio
import json
import yaml
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from agents import ResearcherAgent, ResearchCritic
from learning import ReplayBuffer, SkillDistillation, SelfImprovement

from pathlib import Path
with open(Path(__file__).parent / "config.yaml") as f:
    config = yaml.safe_load(f)

app = FastAPI(title="TITAN Researcher Mode")

researcher = ResearcherAgent(workspace="./experiments")
critic = ResearchCritic()
replay = ReplayBuffer(max_size=config["learning"]["replay_buffer_size"])
distiller = SkillDistillation(threshold=config["learning"]["distillation_threshold"])
self_improve = SelfImprovement()

ws_clients: list[WebSocket] = []

async def broadcast(msg: dict):
    for ws in ws_clients:
        try: await ws.send_json(msg)
        except: ws_clients.remove(ws)

class Observation(BaseModel):
    observation: str
    context: dict = {}

class DataSet(BaseModel):
    data: List[dict]

class ImprovementSuggestion(BaseModel):
    target: str
    new_value: float
    old_value: Optional[float] = None

@app.post("/api/hypothesize")
async def create_hypothesis(req: Observation):
    """Gözlemden hipotez üret."""
    hyp = researcher.formulate_hypothesis(req.observation, req.context)
    
    # Eleştirmen incelemesi
    review = critic.review_hypothesis(hyp.to_dict())
    
    return {
        "hypothesis": hyp.to_dict(),
        "review": review,
    }

@app.post("/api/experiment/{hypothesis_id}")
async def run_experiment(hypothesis_id: str):
    """Bir hipotez için deney tasarla ve çalıştır."""
    # Hipotezi bul
    hyp = next((h for h in researcher.hypotheses if h.id == hypothesis_id), None)
    if not hyp:
        return {"status": "not_found"}
    
    # Deney tasarla
    experiment = researcher.design_experiment(hyp)
    
    # Deneyi çalıştır
    result = researcher.run_experiment(hyp, experiment)
    
    # Replay buffer'a ekle
    replay.add({
        "type": "experiment",
        "hypothesis": hyp.question,
        "score": result["confidence_after"],
        "context": experiment,
        "result": result,
    })
    
    # Beceri damıtma
    if result["status"] == "confirmed" and result["confidence_after"] >= distiller.threshold:
        distiller.distill([{
            "type": hyp.question[:50],
            "score": result["confidence_after"],
            "context": {"hypothesis_id": hyp.id},
            "pattern": hyp.proposed_answer,
            "source": "experiment",
        }])
    
    return {
        "experiment": experiment,
        "result": result,
        "hypothesis_status": hyp.status,
    }

@app.post("/api/discover")
async def discover_patterns(req: DataSet):
    """Veri kümesinden örüntü keşfet."""
    patterns = researcher.discover_patterns(req.data)
    return {"patterns": patterns, "data_points": len(req.data)}

@app.post("/api/web-research")
async def web_research(req: Observation):
    """İnternet üzerinde araştırma yap."""
    result = await researcher.perform_web_research(req.observation)
    return result

@app.get("/api/hypotheses")
async def list_hypotheses(status: Optional[str] = None):
    """Tüm hipotezleri listele."""
    hyps = [h.to_dict() for h in researcher.hypotheses]
    if status:
        hyps = [h for h in hyps if h["status"] == status]
    return {"hypotheses": hyps, "total": len(hyps)}

@app.get("/api/discoveries")
async def list_discoveries():
    """Başarılı keşifleri listele."""
    return {"discoveries": researcher.successful_discoveries}

@app.post("/api/self-improve")
async def improve(req: ImprovementSuggestion):
    """Öz-iyileştirme önerisini değerlendir ve uygula."""
    result = self_improve.apply_improvement({
        "target": req.target,
        "new_value": req.new_value,
        "old_value": req.old_value or 0.5,
    })
    return result

@app.get("/api/skills")
async def list_skills():
    """Damıtılmış becerileri listele."""
    return {"skills": distiller.get_skills()}

@app.get("/api/improvement-suggestions")
async def get_suggestions():
    """Öz-iyileştirme önerileri al."""
    perf = {
        "efficiency": 0.65,
        "learning_rate": 0.008,
    }
    return {"suggestions": self_improve.get_improvement_suggestions(perf)}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mode": "researcher",
        "hypotheses": len(researcher.hypotheses),
        "discoveries": len(researcher.successful_discoveries),
        "skills": len(distiller.skills),
    }

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    ws_clients.append(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "observation":
                hyp = researcher.formulate_hypothesis(msg["observation"])
                await ws.send_json({"type": "hypothesis", "data": hyp.to_dict()})
    except WebSocketDisconnect:
        ws_clients.remove(ws)

if __name__ == "__main__":
    print("🔬 TITAN Researcher Mode başlatılıyor...")
    uvicorn.run("main:app", host=config["server"]["host"], port=config["server"]["port"], reload=True)