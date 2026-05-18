# titan-core/titan/brain/self_education.py
import asyncio
import json
import numpy as np
import random
from typing import List, Dict
from titan.tools.llm import LLMGateway
from titan.executive.meta_goal import MetaGoalEngine, GoalType

class SelfEducationEngine:
    """TITAN'ın kendi kendine öğrenmesini sağlayan motor."""
    
    def __init__(self, llm_gateway: LLMGateway, goal_engine: MetaGoalEngine, memory_vault):
        self.llm = llm_gateway
        self.goals = goal_engine
        self.vault = memory_vault
        self.learning_history: List[Dict] = []
    
    async def identify_knowledge_gap(self) -> str:
        """Sistemin mevcut hedeflerine bakarak 'merak konusu' üretir."""
        try:
            status = self.goals.introspect()
            active_goals = status.get("top_priorities", [])
            goal_desc = active_goals[0]["description"] if active_goals else "Genel sistem gelişimi"
        except:
            goal_desc = "Genel gelişim"
            
        prompt = f"TITAN V4 sistemi olarak şu anki ana hedefim: '{goal_desc}'. Bu hedefi başarmak için hangi teknik veya teorik bilgiye ihtiyacım olabilir? Sadece bir konu başlığı ve kısa bir soru sor."
        
        question = await self.llm.ask(prompt, context="curiosity_generation")
        return question

    async def execute_learning_cycle(self):
        """Öğrenme döngüsünü çalıştırır: Sor -> Öğren -> Planla -> Kaydet."""
        try:
            # 1. Ne öğrenmeliyim?
            question = await self.identify_knowledge_gap()
            if not question or "Hata" in question: 
                return None
            
            print(f"🤔 [EDUCATION] TITAN merak ediyor: {question}")
            
            # 2. LLM'e sor ve öğren
            study_prompt = f"Aşağıdaki soruyu derinlemesine analiz et ve bana adım adım uygulanabilir bir rehber sun: '{question}'"
            lesson = await self.llm.ask(study_prompt, context="deep_learning")
            
            # 3. Öğrenilen bilgiyi plana dök
            planning_prompt = f"Şu bilgiyi öğrendim: '{lesson[:500]}'. Bu bilgiye dayanarak TITAN sistemi için 3 maddelik somut bir aksiyon planı oluştur."
            plan_raw = await self.llm.ask(planning_prompt, context="strategic_planning")
            
            # 4. Hafızaya (Vault) kaydet
            if self.vault:
                self.vault.archive(
                    concept=f"LEARNED: {question[:50]}",
                    vector=np.random.randn(384),
                    metadata={"lesson": lesson[:500], "plan": plan_raw[:500]}
                )
            
            # 5. Hedef motoruna ekle
            self.goals.generate_goal(
                observation=f"Eğitim: {question[:30]}",
                context={"lesson": lesson[:200]},
                goal_type=GoalType.GROWTH
            )
            
            self.learning_history.append({"q": question, "status": "learned"})
            print(f"✅ [EDUCATION] TITAN yeni bir yetenek seti öğrendi.")
            return f"Öğrenilen: {question[:50]}"
        except Exception as e:
            print(f"❌ [EDUCATION] Döngü hatası: {e}")
            return None

    def get_education_report(self) -> Dict:
        return {
            "total_lessons": len(self.learning_history),
            "recent_topics": [h["q"] for h in self.learning_history[-5:]]
        }
