from typing import Dict, List, Optional
import numpy as np
from enum import Enum

class ReasoningStrategy(Enum):
    CHAIN = "chain"
    TREE = "tree"
    GRAPH = "graph"
    ANALOGY = "analogy"
    ABDUCTION = "abduction"

class ReasoningStep:
    def __init__(self, thought: str, confidence: float = 0.5):
        self.thought = thought
        self.confidence = confidence

class ReasoningEngine:
    """TITAN'ın düşünme motoru."""

    def __init__(self, evaluator=None):
        self.reasoning_history: List[Dict] = []
        self.evaluator = evaluator

    def chain_of_thought(self, problem: str, steps: int = 5, action_vec: Optional[np.ndarray] = None) -> List[ReasoningStep]:
        """Problemi adım adım düşün, etik denetim ekle."""
        result = []

        for i in range(steps):
            thought = f"{result[-1].thought} - {problem}" if result else problem
            confidence = 0.9
            evidence = []
            
            if action_vec and self.evaluator:
                eval_result = self.evaluator.evaluate(action_vec, problem)
                ethics_thought = eval_result['feedback']
                confidence += eval_result['total_score']
                evidence.append(ethics_thought)

            result.append(ReasoningStep(thought, confidence))
        return result