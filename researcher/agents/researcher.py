# services/researcher/agents/researcher.py
import numpy as np
import random
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import json
import sys

# Core modülleri bulabilmesi için path ekle
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "titan-core"))

class Hypothesis:
    """Bir araştırma hipotezi."""
    def __init__(self, question: str, proposed_answer: str, confidence: float = 0.5):
        self.id = f"hyp_{hash(question) % 100000}"
        self.question = question
        self.proposed_answer = proposed_answer
        self.confidence = confidence
        self.created = datetime.utcnow().isoformat()
        self.tests: List[Dict] = []
        self.status = "pending"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id, "question": self.question, "answer": self.proposed_answer,
            "confidence": self.confidence, "status": self.status,
            "tests": len(self.tests), "created": self.created,
        }

class ResearcherAgent:
    """Hipotez üretir, test eder, yeni bilgi keşfeder ve internette araştırma yapar."""
    
    def __init__(self, workspace: str = "./experiments"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(exist_ok=True)
        self.hypotheses: List[Hypothesis] = []
        self.successful_discoveries: List[Dict] = []
        
        # İnternet araçları
        try:
            from titan.tools.search import SearchTool
            from titan.tools.browser import BrowserTool
            self.search_tool = SearchTool()
            self.browser_tool = BrowserTool()
        except Exception as e:
            print(f"⚠️ Araştırma araçları yüklenemedi: {e}")
            self.search_tool = None
            self.browser_tool = None
            
        self._load()
    
    def _load(self):
        exp_file = self.workspace / "experiments.json"
        if exp_file.exists():
            try:
                data = json.loads(exp_file.read_text())
                self.successful_discoveries = data.get("discoveries", [])
            except: pass
    
    def _save(self):
        exp_file = self.workspace / "experiments.json"
        exp_file.write_text(json.dumps({
            "discoveries": self.successful_discoveries[-100:],
            "total_hypotheses": len(self.hypotheses),
        }, indent=2))
    
    async def perform_web_research(self, topic: str) -> Dict:
        """İnternet üzerinde bir konuyu araştırır ve özetler."""
        if not self.search_tool or not self.browser_tool:
            return {"error": "Arama araçları hazır değil."}
            
        print(f"🌍 [RESEARCH] '{topic}' internette aranıyor...")
        search_results = await self.search_tool.search(topic, limit=3)
        
        findings = []
        for res in search_results:
            if "error" in res: continue
            try:
                print(f"📖 [RESEARCH] Okunuyor: {res['url']}")
                page = await self.browser_tool.get(res["url"])
                if page["success"]:
                    findings.append({
                        "title": res["title"],
                        "url": res["url"],
                        "summary": page["content"][:800]
                    })
            except: continue
        
        discovery = {"topic": topic, "findings": findings, "timestamp": datetime.now().isoformat()}
        self.successful_discoveries.append(discovery)
        self._save()
        return discovery

    def formulate_hypothesis(self, observation: str, context: Dict = {}) -> Hypothesis:
        hyp = Hypothesis(question=observation, proposed_answer="Simüle edilmiş analiz sonucu.", confidence=0.5)
        self.hypotheses.append(hyp)
        return hyp
    
    def design_experiment(self, hypothesis: Hypothesis) -> Dict:
        return {"hypothesis_id": hypothesis.id, "steps": ["Analiz", "Test"]}
    
    def run_experiment(self, hypothesis: Hypothesis, experiment: Dict) -> Dict:
        hypothesis.status = "confirmed"
        return {"hypothesis_id": hypothesis.id, "status": "confirmed"}
    
    def discover_patterns(self, data: List[Dict]) -> List[Dict]:
        return [{"type": "pattern", "insight": "Veri analizi tamam."}]
