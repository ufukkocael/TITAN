# test_orchestrator_full.py
import asyncio
from titan.integration import TitanOrchestrator

async def main():
    print("TITAN V4 Orchestrator Tam Sürüm Testi\n")
    
    orch = TitanOrchestrator()
    await orch.start()
    
    # Modları bağla (simüle)
    orch.connect_mod("operator")
    orch.connect_mod("programmer")
    orch.connect_mod("researcher")
    orch.connect_mod("companion")
    
    # Test olayları gönder
    await orch.process_event({
        "type": "critical_alert",
        "source": "operator",
        "severity": "CRITICAL",
        "payload": {
            "message": "Kritik bellek sızıntısı tespit edildi",
            "platform": "linux",
            "affected_service": "auth_worker"
        }
    })
    
    await asyncio.sleep(2)
    
    # Durum raporu
    report = orch.get_system_report()
    print(f"\nMod: {report['orchestrator']['mode']}")
    print(f"Kriz: {report['orchestrator']['crisis_level']:.2f}")
    print(f"Hedefler: {report['meta_goals']['active_goals']} aktif")
    print(f"Olaylar: {report['bus']['total_events']}")
    
    # Hızlı durum
    print(f"\n{orch.get_quick_status()}")
    
    await asyncio.sleep(3)
    await orch.shutdown()

asyncio.run(main())