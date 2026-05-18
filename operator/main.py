# services/operator/main.py
import asyncio
import json
import yaml
import sys
import os
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

# Windows asenkron desteği
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# titan-core import'ları
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "titan-core"))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

# Config
BASE_DIR = Path(__file__).parent
with open(BASE_DIR / "config.yaml") as f:
    config = yaml.safe_load(f)

# Collector import'u (platforma göre)
def get_collector():
    if sys.platform == 'win32':
        from collectors.windows import WindowsCollectorAsync
        return WindowsCollectorAsync()
    elif config["collectors"].get("linux") and sys.platform == 'linux':
        from collectors.linux import LinuxCollectorAsync
        return LinuxCollectorAsync()
    elif config["collectors"].get("macos") and sys.platform == 'darwin':
        from collectors.macos import AppleCollectorAsync
        return AppleCollectorAsync()
    else:
        from collectors.simulator import SimulatedCollector
        return SimulatedCollector(platform="simulator", crash_after=30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Operator loop'u başlat
    task = asyncio.create_task(operator_loop())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="TITAN Operator Mode", lifespan=lifespan)

# WebSocket istemcileri
ws_clients: list[WebSocket] = []


async def broadcast(msg: dict):
    """Tüm WebSocket istemcilerine mesaj gönder."""
    dead = []
    for ws in ws_clients:
        try:
            await ws.send_json(msg)
        except:
            dead.append(ws)
    for ws in dead:
        if ws in ws_clients:
            ws_clients.remove(ws)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    ws_clients.append(ws)
    try:
        while True:
            data = await ws.receive_text()
            # Ping-pong veya diğer mesajlar
            await ws.send_json({"type": "pong", "data": "ok"})
    except WebSocketDisconnect:
        if ws in ws_clients:
            ws_clients.remove(ws)


@app.get("/health")
async def health():
    return {"status": "ok", "mode": "operator", "ws_clients": len(ws_clients)}


async def operator_loop():
    """Ana log işleme döngüsü."""
    collector = get_collector()
    print(f"📡 Collector başlatıldı: {collector.__class__.__name__}")
    
    async for log_entry in collector.stream():
        # Dashboard'a gönder
        await broadcast({
            "type": "new_log",
            "data": {
                "platform": log_entry.get("platform", "unknown"),
                "severity": log_entry.get("severity", "INFO"),
                "message": log_entry.get("message", "")[:200],
                "timestamp": log_entry.get("timestamp", datetime.utcnow().isoformat()),
            }
        })
        
        # Kritik uyarıları gateway'e ilet
        if log_entry.get("severity") in ("FATAL", "CRITICAL"):
            await broadcast({
                "type": "alert",
                "data": {
                    "message": log_entry.get("message", ""),
                    "platform": log_entry.get("platform", "unknown"),
                }
            })


if __name__ == "__main__":
    print("🛡️ TITAN Operator Mode başlatılıyor...")
    # Windows'ta asenkron subprocess için Proactor loop'u her koşulda zorla
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        loop_type = "asyncio"
    else:
        loop_type = "auto"
        
    uvicorn.run(
        "main:app", 
        host=config["server"]["host"], 
        port=config["server"]["port"], 
        reload=False, # Reload Windows'ta Proactor policy'i bozabilir
        loop=loop_type
    )