# titan-core/titan/brain/evolution.py
import os
import shutil
import time
import re
from typing import Dict, List, Any
from titan.tools.llm import LLMGateway

class CodeEvolver:
    """TITAN'ın kendi kaynak kodunu analiz edip kontrollü mutasyonlar ürettiği motor."""
    
    def __init__(self, llm_gateway: LLMGateway, governance_guard=None):
        self.llm = llm_gateway
        self.guard = governance_guard
        self.evolution_log: List[Dict] = []
        self.target_files = [
            "titan/core/tesseract.py",
            "titan/brain/evaluator.py",
            "titan/brain/reasoning.py",
            "titan/stability/antifragility.py"
        ]
        self.root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    async def scan_self(self):
        import random
        target = random.choice(self.target_files)
        file_path = os.path.join(self.root_path, target)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"path": target, "full_path": file_path, "content": content}
        except: return {"error": "Fail"}

    def _extract_code(self, raw_text):
        """Markdown bloklarından veya karma metinden sadece geçerli Python kodunu çeker."""
        if not raw_text: return ""
        
        # 1. ```python ... ``` bloğunu ara
        py_match = re.search(r"```python\s*(.*?)\s*```", raw_text, re.DOTALL)
        if py_match:
            return py_match.group(1).strip()
            
        # 2. Herhangi bir ``` ... ``` bloğunu ara
        any_match = re.search(r"```\s*(.*?)\s*```", raw_text, re.DOTALL)
        if any_match:
            return any_match.group(1).strip()
            
        # 3. Eğer blok yoksa, kodun başladığı yeri tahmin et (Regex ile satır başlarını tara)
        lines = raw_text.splitlines()
        code_lines = []
        started = False
        for line in lines:
            # Kod genellikle import, def, class veya yorum satırı ile başlar
            if not started and re.match(r"^(import |from |def |class |#|@)", line.strip()):
                started = True
            if started:
                code_lines.append(line)
        
        if code_lines:
            return "\n".join(code_lines).strip()
            
        return raw_text.strip()

    async def propose_evolution(self, file_data):
        prompt = (f"Sen TITAN V4 Evrim Motorusun. Geliştiricin U.KOCAEL.\n"
                  f"DOSYA: {file_data['path']}\n"
                  f"Aşağıdaki Python kodunu analiz et ve daha performanslı, 'akıllı' bir REFACTOR yap.\n"
                  f"ÖNEMLİ: SADECE Python kodunu ver, açıklama yapma. Yanıtını ```python ... ``` içine al.\n\n"
                  f"MEVCUT KOD:\n{file_data['content'][:1500]}")
        
        resp = await self.llm.ask(prompt, context="recursive_evolution")
        code = self._extract_code(resp)
            
        mutation = {
            "original_path": file_data["full_path"],
            "relative_path": file_data["path"],
            "mutation_code": code,
            "generation": len(self.evolution_log) + 1,
            "timestamp": time.time(),
            "governance": {"approved": True}
        }

        if self.guard:
            mutation["governance"] = self.guard.validate_mutation(mutation["relative_path"], mutation["mutation_code"])
            
        return mutation

    def create_shadow_file(self, mutation):
        if not mutation["governance"].get("approved"): return False
        try:
            with open(mutation["original_path"] + ".shadow", 'w', encoding='utf-8') as f:
                f.write(mutation["mutation_code"])
            return True
        except: return False

    def resolve_eclipse(self, mutation):
        if not mutation["governance"].get("approved"): return False
        try:
            orig = mutation["original_path"]
            shutil.copy2(orig, orig + ".bak")
            shutil.move(orig + ".shadow", orig)
            self.evolution_log.append(mutation)
            return True
        except: return False
