# services/programmer/main.py
import asyncio
import json
import yaml
import sys
import os
from pathlib import Path

# Windows asenkron alt süreç desteği
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import uvicorn

from agents import CoderAgent, CriticAgent, TesterAgent
from tools.git import GitTool
from tools.patch_generator import PatchGenerator

# Config
from pathlib import Path
BASE_DIR = Path(__file__).parent
with open(BASE_DIR / "config.yaml") as f:
    config = yaml.safe_load(f)

app = FastAPI(title="TITAN Programmer Mode")

# Ajanlar
coder = CoderAgent(workspace=config["sandbox"]["workspace"])
critic = CriticAgent()
tester = TesterAgent()
git = GitTool(
    repo_path=config["sandbox"]["workspace"],
    user=config["git"]["user"],
    email=config["git"]["email"]
)
patcher = PatchGenerator()

ws_clients: list[WebSocket] = []

async def broadcast(msg: dict):
    for ws in ws_clients:
        try: await ws.send_json(msg)
        except: ws_clients.remove(ws)

class FixRequest(BaseModel):
    error_message: str
    file_path: str = ""
    line_number: int = 0
    context: dict = {}

class CodeRequest(BaseModel):
    specification: str
    language: str = "python"

class ReviewRequest(BaseModel):
    code: str
    context: dict = {}

@app.post("/api/fix")
async def fix_error(req: FixRequest):
    """Hata mesajı al, yama üret, uygula."""
    
    # 1. Hatayı teşhis et
    diagnosis = coder.analyze_error(req.error_message)
    
    # 2. Yama türünü bul
    error_type = patcher.diagnose(req.error_message)
    if not error_type:
        error_type = diagnosis["type"]
    
    # 3. Yama üret
    variables = req.context if req.context else {"var": "ptr", "error_code": "-1", "size": "1024"}
    patch_line = patcher.generate(error_type, variables)
    
    if not patch_line:
        patch_line = coder.generate_fix(error_type, req.file_path, req.line_number, variables)
    
    if not patch_line:
        return {"status": "no_fix_available", "diagnosis": diagnosis}
    
    # 4. Eleştirmen onayı
    review = critic.review(patch_line)
    if not review["approved"] and config["review"]["require_critic_approval"]:
        return {
            "status": "rejected_by_critic",
            "diagnosis": diagnosis,
            "review": review,
        }
    
    # 5. Uygula
    success = coder.apply_patch(req.file_path, req.line_number, patch_line)
    
    return {
        "status": "applied" if success else "failed",
        "diagnosis": diagnosis,
        "patch": patch_line,
        "review": review,
    }

@app.post("/api/generate")
async def generate_code(req: CodeRequest):
    """Spesifikasyondan kod üret."""
    result = coder.write_code(req.specification, req.language)
    
    # Eleştirmen kontrolü
    if result["status"] == "generated":
        code = Path(result["file"]).read_text()
        review = critic.review(code, {"purpose": req.specification})
        result["review"] = review
    
    return result

@app.post("/api/review")
async def review_code(req: ReviewRequest):
    """Kod incelemesi yap."""
    result = critic.review(req.code, req.context)
    return result

@app.post("/api/pr")
async def create_pull_request(title: str, body: str = ""):
    """Değişiklikleri PR olarak gönder."""
    branch = f"titan-fix-{hash(title) % 10000}"
    
    result = git.create_branch(branch)
    if not result["success"]:
        return {"status": "failed", "error": result["stderr"]}
    
    result = git.commit(title)
    if not result["success"]:
        return {"status": "commit_failed", "error": result["stderr"]}
    
    result = git.push(branch)
    if not result["success"]:
        return {"status": "push_failed", "error": result["stderr"]}
    
    result = git.create_pr(title, body or "TITAN tarafından otomatik üretildi.")
    return {"status": "success", "branch": branch, "pr_url": result.get("stdout", "")}

@app.get("/health")
async def health():
    return {"status": "ok", "mode": "programmer"}

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    ws_clients.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_clients.remove(ws)

if __name__ == "__main__":
    # Windows'ta asenkron subprocess için loop'u zorla
    loop_type = "asyncio" if sys.platform == "win32" else "auto"
    uvicorn.run(
        "main:app", 
        host=config["server"]["host"], 
        port=config["server"]["port"], 
        reload=True,
        loop=loop_type
    )