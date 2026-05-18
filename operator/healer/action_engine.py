# services/operator/healer/action_engine.py
import asyncio
from .safety import SafetyGate, ActionLevel
from .actions import HealerActions

class ActionEngine:
    def __init__(self, approval_callback=None):
        self.actions = HealerActions()
        self.gate = SafetyGate()
        self.approval_callback = approval_callback
    
    async def execute(self, recommendation: dict) -> dict:
        action = recommendation.get("action", "")
        target = recommendation.get("target", "")
        platform = recommendation.get("platform", "linux")
        version = recommendation.get("version", "")
        
        level = self.gate.classify(action, target)
        
        if self.gate.require_approval(level):
            if self.approval_callback:
                if not await self.approval_callback(recommendation, level):
                    return {"status": "rejected", "reason": "İnsan onayı bekleniyor"}
        
        try:
            if action == "restart":
                result = await self.actions.restart_service(target, platform)
            elif action == "rollback":
                result = await self.actions.rollback_package(target, version, platform)
            elif action == "block_ip":
                ip = recommendation.get("ip")
                result = await self.actions.block_ip(ip, platform)
            else:
                result = f"Unknown action: {action}"
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "failed", "error": str(e)}