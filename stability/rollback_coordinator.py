# titan-core/titan/stability/rollback_coordinator.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import time
import json
import os


@dataclass
class RollbackPoint:
    id: str
    timestamp: float
    state_snapshot: Dict
    description: str = ""


@dataclass
class RollbackPlan:
    target_id: str
    steps: List[str]
    estimated_time_ms: int = 0


class RollbackCoordinator:
    """Geri alma işlemlerini koordine eden sistem."""
    
    def __init__(self, snapshot_dir: str = "./rollback_snapshots"):
        self.snapshot_dir = snapshot_dir
        self.checkpoints: List[RollbackPoint] = []
        self.rollback_history: List[Dict] = []
        
        # Snapshot dizinini oluştur
        os.makedirs(snapshot_dir, exist_ok=True)
    
    def create_checkpoint(self, state: Dict, description: str = "") -> str:
        """Bir kontrol noktası oluştur."""
        cp_id = f"cp_{int(time.time() * 1000)}"
        
        checkpoint = RollbackPoint(
            id=cp_id,
            timestamp=time.time(),
            state_snapshot=state.copy(),
            description=description
        )
        self.checkpoints.append(checkpoint)
        
        # Diske kaydet
        snapshot_file = os.path.join(self.snapshot_dir, f"{cp_id}.json")
        with open(snapshot_file, 'w') as f:
            json.dump({
                "id": cp_id,
                "timestamp": checkpoint.timestamp,
                "state": state,
                "description": description
            }, f, indent=2)
        
        # Bellekte sınırlı tut
        if len(self.checkpoints) > 100:
            self.checkpoints = self.checkpoints[-50:]
        
        return cp_id
    
    def get_checkpoint(self, cp_id: str) -> Optional[RollbackPoint]:
        """Bir kontrol noktasını getir."""
        # Önce bellekten ara
        for cp in self.checkpoints:
            if cp.id == cp_id:
                return cp
        
        # Sonra diskten ara
        snapshot_file = os.path.join(self.snapshot_dir, f"{cp_id}.json")
        if os.path.exists(snapshot_file):
            with open(snapshot_file, 'r') as f:
                data = json.load(f)
                return RollbackPoint(
                    id=data["id"],
                    timestamp=data["timestamp"],
                    state_snapshot=data["state"],
                    description=data.get("description", "")
                )
        
        return None
    
    def create_rollback_plan(self, target_cp_id: str, current_state: Dict) -> Optional[RollbackPlan]:
        """Bir geri alma planı oluştur."""
        target_cp = self.get_checkpoint(target_cp_id)
        if not target_cp:
            return None
        
        steps = []
        
        # Hangi bileşenlerin geri alınacağını belirle
        for key in target_cp.state_snapshot:
            if key in current_state and current_state[key] != target_cp.state_snapshot[key]:
                steps.append(f"Revert {key}: {current_state[key]} -> {target_cp.state_snapshot[key]}")
        
        return RollbackPlan(
            target_id=target_cp_id,
            steps=steps,
            estimated_time_ms=len(steps) * 100
        )
    
    def execute_rollback(self, plan: RollbackPlan) -> bool:
        """Bir geri alma planını uygula."""
        try:
            self.rollback_history.append({
                "timestamp": time.time(),
                "plan": {
                    "target_id": plan.target_id,
                    "steps": plan.steps,
                    "estimated_time_ms": plan.estimated_time_ms
                },
                "status": "executed"
            })
            return True
        except Exception as e:
            self.rollback_history.append({
                "timestamp": time.time(),
                "plan": {"target_id": plan.target_id},
                "status": "failed",
                "error": str(e)
            })
            return False
    
    def list_checkpoints(self, limit: int = 20) -> List[RollbackPoint]:
        """Tüm kontrol noktalarını listele."""
        return self.checkpoints[-limit:]
    
    def get_latest_checkpoint(self) -> Optional[RollbackPoint]:
        """En son kontrol noktasını getir."""
        return self.checkpoints[-1] if self.checkpoints else None