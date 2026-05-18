# titan-core/titan/brain/predictor.py
import numpy as np
from typing import Dict, List, Optional
import time

class ActionPredictor:
    """Sistemin eylem sonuçlarını ve gelecek durumları tahmin eden motor."""
    
    def __init__(self):
        self.prediction_history: List[Dict] = []
        self.model_confidence = 0.5
    
    def predict_next_state(self, current_state: Dict, action: str) -> Dict:
        """Mevcut durum ve eylemden bir sonraki olası durumu tahmin eder."""
        # Basit bir tahmin mantığı (gerçekte RNN veya Transformer tabanlı olabilir)
        prediction = current_state.copy()
        prediction["timestamp"] = time.time()
        
        if "restart" in action:
            prediction["status"] = "restarting"
            prediction["load"] = 0.1
        elif "fix" in action:
            prediction["status"] = "patching"
            prediction["error_count"] = max(0, prediction.get("error_count", 1) - 1)
        
        return {
            "predicted_state": prediction,
            "confidence": self.model_confidence,
            "estimated_time_ms": 150
        }
    
    def evaluate_prediction(self, predicted: Dict, actual: Dict):
        """Tahminin ne kadar doğru olduğunu ölçer ve modeli günceller."""
        # Tahmin hatasını ölç (basit fark)
        error = 0.0
        keys = set(predicted.keys()) & set(actual.keys())
        for k in keys:
            if isinstance(predicted[k], (int, float)) and isinstance(actual[k], (int, float)):
                error += abs(predicted[k] - actual[k])
        
        # Güven skorunu güncelle
        if error < 0.1:
            self.model_confidence = min(1.0, self.model_confidence + 0.05)
        else:
            self.model_confidence = max(0.1, self.model_confidence - 0.05)
            
        self.prediction_history.append({
            "error": error,
            "confidence_after": self.model_confidence,
            "timestamp": time.time()
        })
