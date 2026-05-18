# titan-core/titan/tools/firewall.py
import asyncio
import os
from typing import Dict, List

class FirewallTool:
    """TITAN'ın savunma hattı. IP bloklama ve kural yönetimi yapar."""
    
    def __init__(self, platform: str = "linux"):
        self.platform = platform
        self.blocked_ips: List[str] = []
    
    async def block_ip(self, ip: str, reason: str = "unauthorized_access") -> Dict:
        """Belirli bir IP adresini sisteme erişimden men eder."""
        if ip in self.blocked_ips:
            return {"success": True, "message": f"{ip} zaten bloklu."}
        
        # Gerçek dünyada platforma göre iptables, ufw veya cloud API kullanılır
        cmd = []
        if self.platform == "linux":
            # Örnek: sudo iptables -A INPUT -s IP -j DROP
            cmd = ["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
        elif self.platform == "windows":
            # Örnek: netsh advfirewall firewall add rule ...
            cmd = ["netsh", "advfirewall", "firewall", "add", "rule", 
                   f"name=TITAN_BLOCK_{ip}", "dir=in", "action=block", f"remoteip={ip}"]
        
        # Simülasyon modunda (root değilsek veya testteysek) sadece logla
        print(f"🛡️ [FIREWALL] Bloklanıyor: {ip} | Neden: {reason}")
        
        try:
            # Gerçek komut çalıştırma (Dikkat: sudo yetkisi gerektirir)
            # if cmd:
            #     proc = await asyncio.create_subprocess_exec(*cmd)
            #     await proc.wait()
            
            self.blocked_ips.append(ip)
            return {
                "success": True, 
                "ip": ip, 
                "reason": reason, 
                "platform": self.platform,
                "action": "blocked"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_blocked_ips(self) -> List[str]:
        return self.blocked_ips
    
    async def unblock_ip(self, ip: str) -> Dict:
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            print(f"🔓 [FIREWALL] Blok kaldırıldı: {ip}")
            return {"success": True, "ip": ip, "action": "unblocked"}
        return {"success": False, "message": "IP bulunamadı."}
