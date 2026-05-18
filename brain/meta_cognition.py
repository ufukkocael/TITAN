# titan-core/titan/brain/meta_cognition.py (SCATTERED hatası düzeltildi)
import time
from typing import Dict, List, Optional
from enum import Enum


class CognitiveState(Enum):
    FOCUSED = "focused"
    SCATTERED = "scattered"      # DÜZELTİLDİ: SCATTERED -> scattered
    OVERLOADED = "overloaded"
    DOUBTFUL = "doubtful"
    CERTAIN = "certain"


class MetaCognitionController:
    """TITAN'ın kendi düşünme süreçlerini izleyen ve optimize eden katman."""
    
    def __init__(self):
        self.cognition_history: List[Dict] = []
        self.current_strategy = "chain_of_thought"
        self.doubt_threshold = 0.4
    
    def monitor_process(self, reasoning_chain: List, performance_metrics: Dict) -> Dict:
        """Mantık yürütme sürecini analiz eder."""
        avg_confidence = sum(s.confidence for s in reasoning_chain) / len(reasoning_chain) if reasoning_chain else 0
        
        state = CognitiveState.FOCUSED
        if performance_metrics.get("latency", 0) > 500:
            state = CognitiveState.OVERLOADED
        elif avg_confidence < self.doubt_threshold:
            state = CognitiveState.DOUBTFUL
        elif len(reasoning_chain) > 10:
            state = CognitiveState.SCATTERED  # Artık çalışıyor!
        
        insight = {
            "timestamp": time.time(),
            "state": state.value,
            "confidence": avg_confidence,
            "steps_analyzed": len(reasoning_chain),
            "adjustment_needed": state in (CognitiveState.DOUBTFUL, CognitiveState.OVERLOADED, CognitiveState.SCATTERED)
        }
        self.cognition_history.append(insight)
        return insight
    
    def suggest_strategy(self, problem_type: str) -> str:
        """Problemin türüne göre en iyi düşünme metodunu seçer."""
        if problem_type == "creative":
            return "lateral_thinking"
        elif problem_type == "urgent":
            return "heuristic_shortcut"
        return "chain_of_thought"