# api/gateway/main.py
import asyncio
import yaml
import os
import time
import sys
import httpx
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect, Form, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path

# Windows Proactor Loop Fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

START_TIME = time.time()
BASE_DIR = Path(__file__).parent
with open(BASE_DIR / "config.yaml") as f:
    config = yaml.safe_load(f)

from middleware.auth import AuthMiddleware
from routes import ServiceProxy

app = FastAPI(title="TITAN V4 API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="http://(localhost|127\\.0\\.0\\.1):.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth = AuthMiddleware(config["auth"]["jwt_secret"], config["auth"]["token_expiry"])

service_urls = {
    "operator": config["services"]["operator"]["url"],
    "programmer": config["services"]["programmer"]["url"],
    "researcher": config["services"]["researcher"]["url"],
    "companion": config["services"]["companion"]["url"],
    "orchestrator": config["services"]["orchestrator"]["url"],
}
proxy = ServiceProxy(service_urls)
ws_clients: list[WebSocket] = []

# --- KRİTİK: İÇ LOG YOLU (AUTH YOK) ---
@app.post("/internal/publish")
async def gateway_publish(message: dict):
    """Sistem içi log yayını - Güvenlikten muaf."""
    for client in ws_clients[:]:
        try: await client.send_json(message)
        except: pass
    return {"status": "ok"}

@app.get("/health")
async def health():
    results = {}
    async with httpx.AsyncClient(timeout=2) as client:
        for name, url in service_urls.items():
            try:
                resp = await client.get(f"{url}/health")
                results[name] = "healthy" if resp.status_code == 200 else "unhealthy"
            except: results[name] = "unreachable"
    return {"services": results, "uptime": time.time() - START_TIME}

@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "titan2026":
        return {"access_token": auth.create_token({"sub": username}), "token_type": "bearer"}
    raise HTTPException(status_code=401)

# --- PROXY ---
@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(service: str, path: str, request: Request):
    if config["auth"]["enabled"]:
        public_paths = ["health", "login", "register"]
        if not any(path.startswith(p) for p in public_paths):
            await auth.authenticate(request)
    
    body = None
    if request.method in ("POST", "PUT"):
        try: body = await request.json()
        except: body = {}
    
    return await proxy.forward(service, request.method, path, body, dict(request.headers))

@app.websocket("/ws/gateway")
async def gateway_websocket(ws: WebSocket):
    await ws.accept()
    ws_clients.append(ws)
    try:
        while True: await ws.receive_json()
    except: pass
    finally:
        if ws in ws_clients: ws_clients.remove(ws)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=False)
