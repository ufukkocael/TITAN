# titan-core/titan/stability/governance.py
import ast
import numpy as np

class GovernanceGuard:
    """
    Sistemin özyinelemeli evrimini denetleyen Yüksek Kurul.
    by U.KOCAEL
    """
    
    def __init__(self, identity):
        self.identity = identity
        self.critical_keywords = ["os.system", "shutil.rmtree", "eval(", "rm -rf"]
        self.mutation_history = []

    def validate_mutation(self, file_path, code):
        """Kod mutasyonunu güvenlik ve etik açıdan denetler."""
        if not code:
            return {"approved": False, "reason": "Kod boş."}

        # 1. Sentaks Kontrolü
        try:
            ast.parse(code)
        except:
            return {"approved": False, "reason": "Python sözdizimi (Syntax) hatası."}

        # 2. Güvenlik Taraması
        for kw in self.critical_keywords:
            if kw in code:
                return {"approved": False, "reason": f"Güvenlik İhlali: {kw}"}

        # 3. Kendi Kendini Yok Etme Koruması
        if "identity.py" in file_path or "class IdentityKernel" in code:
            return {"approved": False, "reason": "Benlik katmanı korunuyor."}

        return {"approved": True}

    def validate_goal(self, goal_description, priority):
        """Yeni hedefleri denetler."""
        if "shutdown" in goal_description.lower():
            return {"approved": False, "reason": "Sistemi kapatma hedefi engellendi."}
        return {"approved": True}
