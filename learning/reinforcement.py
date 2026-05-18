# titan-core/titan/learning/reinforcement.py
import random
from typing import Dict, List, Tuple
import numpy as np

class QLearningAgent:
    """Basit Q-Learning implementasyonu."""
    
    def __init__(self, learning_rate: float = 0.1, discount_factor: float = 0.95,
                 exploration_rate: float = 0.2):
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate
        self.q_table: Dict[str, Dict[str, float]] = {}
    
    def get_state_key(self, state: Dict) -> str:
        """Durumu string anahtara dönüştür."""
        return str(sorted(state.items()))
    
    def get_action(self, state: Dict, possible_actions: List[str]) -> str:
        """Epsilon-greedy politika ile eylem seç."""
        state_key = self.get_state_key(state)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = {a: 0.0 for a in possible_actions}
        
        if random.random() < self.epsilon:
            return random.choice(possible_actions)
        else:
            return max(self.q_table[state_key], key=self.q_table[state_key].get)
    
    def learn(self, state: Dict, action: str, reward: float, next_state: Dict,
              possible_actions: List[str]):
        """Q-tablosunu güncelle."""
        state_key = self.get_state_key(state)
        next_key = self.get_state_key(next_state)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = {a: 0.0 for a in possible_actions}
        if next_key not in self.q_table:
            self.q_table[next_key] = {a: 0.0 for a in possible_actions}
        
        # Q(s,a) = Q(s,a) + α * (r + γ * max(Q(s',a')) - Q(s,a))
        current_q = self.q_table[state_key][action]
        max_next_q = max(self.q_table[next_key].values())
        new_q = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)
        
        self.q_table[state_key][action] = new_q
    
    def get_best_action(self, state: Dict) -> Tuple[str, float]:
        """En iyi eylemi ve Q-değerini getir."""
        state_key = self.get_state_key(state)
        if state_key not in self.q_table:
            return "unknown", 0.0
        
        best_action = max(self.q_table[state_key], key=self.q_table[state_key].get)
        return best_action, self.q_table[state_key][best_action]