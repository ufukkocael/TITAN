# services/orchestrator/main.py
import asyncio
import json
import yaml
import sys
import os
import httpx
import time
import random
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

# Project Root
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "titan-core"))

# Global Instances
orchestrator = antifragility = bridge = crystals = llm = goals = creativity = None
dream = education = maintenance = evolver = maestro = guard = quantum = ingest_tool = learning_vault = validator = None

# Core Imports
try:
    from titan.core import TesseractOrchestrator
    from titan.stability import AntifragilityEngine, GovernanceGuard, EvolutionValidator
    from titan.brain.evolution import CodeEvolver
    from titan.brain.identity import IdentityKernel
    from titan.bridge import TitanBridge
    from titan.core.crystal import CrystalLibrary
    from titan.tools.llm import LLMGateway
    from titan.executive.meta_goal import MetaGoalEngine
    from titan.brain.creativity import CreativityEngine
    from titan.brain.dream import DreamLayer
    from titan.brain.self_education import SelfEducationEngine
    from titan.memory.vault import WisdomVault
    from titan.memory.forget import MemoryMaintenance
    from titan.core.maestro import Maestro
    from titan.core.quantum import QuantumVectorEngine
    from titan.tools.ingest import DocumentIngestTool
    from titan.learning.vault import LearningVault
except Exception as e:
    print(f"❌ Titan Core yükleme hatası: {e}")
    TesseractOrchestrator = AntifragilityEngine = GovernanceGuard = EvolutionValidator = None
    CodeEvolver = IdentityKernel = TitanBridge = CrystalLibrary = LLMGateway = None
    MetaGoalEngine = CreativityEngine = DreamLayer = SelfEducationEngine = WisdomVault = None
    MemoryMaintenance = Maestro = QuantumVectorEngine = DocumentIngestTool = LearningVault = None

# Config
BASE_DIR = Path(__file__).parent
with open(BASE_DIR / "config.yaml") as f:
    config = yaml.safe_load(f)

GATEWAY_URL = config.get("gateway_url", "http://localhost:9000")

async def broadcast_log(platform, message, severity="INFO"):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{GATEWAY_URL}/internal/publish", json={
                "type": "new_log",
                "data": {"platform": platform, "message": message, "severity": severity, "timestamp": time.time()}
            })
    except: pass

async def broadcast_telemetry():
    """Dashboard metriklerini anlık günceller."""
    await asyncio.sleep(10)
    while True:
        try:
            if orchestrator:
                data = {
                    "active_nodes": len(orchestrator.nodes),
                    "crystals": len(crystals.crystals) if crystals else 0,
                    "generation": len(evolver.evolution_log) if evolver else 0,
                    "training_samples": learning_vault.get_stats().get("total_samples", 0) if learning_vault else 0,
                    "governance_score": 1.0 if guard else 0.0,
                    "maestro_dynamic": maestro.get_score().get("baton", {}).get("dynamic", "MEZZO") if maestro else "OFF"
                }
                async with httpx.AsyncClient(timeout=1.0) as client:
                    await client.post(f"{GATEWAY_URL}/internal/publish", json={
                        "type": "telemetry_update",
                        "data": data
                    })
        except: pass
        await asyncio.sleep(5)

async def cognitive_loop():
    await asyncio.sleep(5)
    await broadcast_log("CORE", "🧠 TITAN 4.0 Bilinç Döngüsü Aktif.")
    
    while True:
        try:
            if antifragility:
                vaccine = antifragility.check_system_health()
                if vaccine: 
                    await broadcast_log("STABILITY", f"💉 {vaccine}", "WARN")
                    crystals.distill(f"Vaccine_{int(time.time())}", np.random.randn(384), source="Antifragility")
            
            if evolver and guard and validator:
                self_scan = await evolver.scan_self()
                if self_scan and "content" in self_scan:
                    mutation = await evolver.propose_evolution(self_scan)
                    
                    # 1. Governance Check (Yasal mı?)
                    gov_check = mutation.get("governance", {"approved": False})
                    
                    if gov_check["approved"]:
                        # 2. Validation Check (Mantıklı ve Doğru mu?)
                        await broadcast_log("VALIDATION", f"🧐 Mutasyon denetleniyor: {mutation['relative_path']}")
                        
                        # Interface check
                        iface = validator.check_interface_consistency(self_scan["content"], mutation["mutation_code"])
                        if not iface["valid"]:
                            await broadcast_log("VALIDATION", f"🛑 Mantıksal Red: {iface['reason']}", "ERROR")
                            continue
                            
                        # Logical Audit (LLM Denetimi)
                        audit = await validator.logical_audit(llm, mutation["relative_path"], mutation)
                        if not audit["approved"]:
                            await broadcast_log("VALIDATION", f"🛑 Audit Red: {audit['reason']}", "ERROR")
                            continue

                        # 3. Apply Shadow
                        if evolver.create_shadow_file(mutation):
                            await broadcast_log("EVOLUTION", f"🌑 Gölge kod doğrulandı: {mutation['relative_path']}")
                            if random.random() < 0.2:
                                if evolver.resolve_eclipse(mutation):
                                    await broadcast_log("ECLIPSE", f"✨ {mutation['relative_path']} evrimleşti!", "WARN")
                                    crystals.distill(f"Evo_{mutation['generation']}", np.random.randn(384), source="Evolution")
                    else:
                        await broadcast_log("GOVERNANCE", f"🛑 Red: {gov_check['reason']}", "ERROR")

            if education:
                res = await education.execute_learning_cycle()
                if res: 
                    await broadcast_log("EDUCATION", f"🎓 {res}", "INFO")
                    crystals.distill(f"Wis_{int(time.time())}", np.random.randn(384), source="Education")
            
            if orchestrator: 
                new_node = orchestrator.add_node(f"THOUGHT_{int(time.time())}", np.random.randn(384), w=0.8)
                if quantum and len(orchestrator.nodes) > 10:
                    target = random.choice(orchestrator.nodes[:-1])
                    quantum.entangle(new_node.concept, target.concept)
                    await broadcast_log("QUANTUM", f"⚛️ Dolanıklık: {new_node.concept} <-> {target.concept}")
            
            await asyncio.sleep(20) 
        except Exception as e: 
            await broadcast_log("CORE", f"❌ Hata: {e}", "CRITICAL")
            await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator, antifragility, bridge, crystals, llm, goals, creativity, dream, education, maintenance, evolver, maestro, guard, quantum, ingest_tool, learning_vault, validator
    
    if TesseractOrchestrator:
        mem_dir = ROOT_DIR / "titan_memory"
        mem_dir.mkdir(exist_ok=True)
        
        llm = LLMGateway(config.get("llm", {}))
        identity = IdentityKernel()
        guard = GovernanceGuard(identity)
        validator = EvolutionValidator() # Yeni doğrulayıcı
        
        orchestrator = TesseractOrchestrator(storage_path=str(mem_dir / "tesseract.pkl"))
        crystals = CrystalLibrary(storage_path=str(mem_dir / "crystals.pkl"))
        learning_vault = LearningVault(storage_path=str(ROOT_DIR / "data" / "training_set.jsonl"))
        
        goals = MetaGoalEngine(governance_guard=guard)
        creativity = CreativityEngine(orchestrator)
        evolver = CodeEvolver(llm, governance_guard=guard)
        antifragility = AntifragilityEngine(evolver, crystals)
        dream = DreamLayer(orchestrator, creativity)
        maintenance = MemoryMaintenance()
        bridge = TitanBridge(orchestrator, memory_path=str(mem_dir))
        education = SelfEducationEngine(llm, goals, bridge.vault)
        quantum = QuantumVectorEngine(dimension=384)
        ingest_tool = DocumentIngestTool()
        
        maestro = Maestro(sys.modules[__name__])
        asyncio.create_task(maestro.conduct())
        asyncio.create_task(cognitive_loop())
        asyncio.create_task(broadcast_telemetry())
        
        print("🚀 Orchestrator başlatıldı.")
    yield

app = FastAPI(title="TITAN V4 Orchestrator", lifespan=lifespan)

@app.get("/health")
async def health(): 
    if not orchestrator: return {"status": "initializing"}
    return {"status": "healthy"}

@app.get("/api/telemetry")
async def get_telemetry():
    if not orchestrator: return {"status": "init"}
    return {
        "active_nodes": len(orchestrator.nodes),
        "crystals": len(crystals.crystals) if crystals else 0,
        "generation": len(evolver.evolution_log) if evolver else 0,
        "training_samples": learning_vault.get_stats().get("total_samples", 0) if learning_vault else 0,
        "maestro_dynamic": maestro.get_score().get("baton", {}).get("dynamic", "MEZZO") if maestro else "OFF"
    }

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    uvicorn.run("main:app", host="0.0.0.0", port=9005, reload=False)
