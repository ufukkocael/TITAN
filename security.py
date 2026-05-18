# titan-core/titan/security.py
from enum import Enum

class ActionLevel(Enum):
    SAFE = 1
    CONDITIONAL = 2
    DANGEROUS = 3

class SafetyGate:
    @staticmethod
    def classify(action: str, target: str) -> ActionLevel:
        dangerous = ["rollback", "delete", "format", "drop"]
        conditional = ["update", "install", "restart"]
        if any(d in action.lower() for d in dangerous):
            return ActionLevel.DANGEROUS
        if any(c in action.lower() for c in conditional):
            return ActionLevel.CONDITIONAL
        return ActionLevel.SAFE
    
    @staticmethod
    def require_approval(level: ActionLevel) -> bool:
        return level != ActionLevel.SAFE