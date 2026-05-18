# services/companion/main.py
import asyncio
import json
import yaml
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
import uvicorn
from pathlib import Path

from agents import CompanionAgent, MemoryKeeper

# Config
BASE_DIR = Path(__file__).parent
with open(BASE_DIR / "config.yaml") as f:
    config = yaml.safe_load(f)

# Global değişkenler
companion = None
memory = None
ws_clients: list[WebSocket] = []
voice_available = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager - startup ve shutdown işlemleri için."""
    global companion, memory, voice_available
    
    # --- STARTUP ---
    print("🤖 TITAN Companion başlatılıyor...")
    
    # Ajanları oluştur
    companion = CompanionAgent(config["companion"])
    memory = companion.memory
    
    # Ses kontrolü
    voice_available = False
    
    # Ollama bağlantısını kontrol et
    await companion.initialize()
    
    yield  # Bu noktada uygulama çalışır
    
    # --- SHUTDOWN ---
    print("🛑 TITAN Companion kapatılıyor...")
    for ws in ws_clients[:]:
        try:
            await ws.close()
        except:
            pass
    ws_clients.clear()


# FastAPI app
app = FastAPI(
    title="TITAN Companion Mode",
    lifespan=lifespan
)


class ChatRequest(BaseModel):
    message: str
    context: dict = {}
    provider: Optional[str] = None
    api_key: Optional[str] = None


class ProfileUpdate(BaseModel):
    key: str
    value: str


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Kullanıcı mesajına yanıt ver."""
    # NOT: CompanionAgent.respond artık llm_provider ve llm_api_key bekliyor
    result = await companion.respond(
        user_message=req.message, 
        llm_provider=req.provider, 
        llm_api_key=req.api_key
    )
    
    # WebSocket'e bildir
    for ws in ws_clients[:]:
        try:
            await ws.send_json({"type": "chat", "data": result})
        except:
            if ws in ws_clients:
                ws_clients.remove(ws)
    
    return result


@app.get("/api/relationship")
async def relationship():
    return memory.get_relationship_status()


@app.post("/api/profile")
async def update_profile(req: ProfileUpdate):
    memory.update_profile(req.key, req.value)
    return {"status": "updated"}


@app.get("/api/memory")
async def search_memory(query: str = ""):
    if not query:
        return {"results": []}
    return {"results": memory.recall_context(query)}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mode": "companion",
        "ws_clients": len(ws_clients),
    }


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    ws_clients.append(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "chat":
                # Match the respond signature
                result = await companion.respond(
                    user_message=msg.get("message", ""),
                    llm_provider=msg.get("provider"),
                    llm_api_key=msg.get("api_key")
                )
                await ws.send_json({"type": "chat_response", "data": result})
            elif msg.get("type") == "ping":
                await ws.send_json({"type": "pong"})
    except WebSocketDisconnect:
        if ws in ws_clients:
            ws_clients.remove(ws)
    except:
        if ws in ws_clients:
            ws_clients.remove(ws)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config["server"]["host"],
        port=config["server"]["port"],
        reload=False  # Windows'ta reload bazen loop sorunlarına yol açıyor
    )
