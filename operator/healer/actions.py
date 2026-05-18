# services/operator/healer/actions.py
import asyncio

class HealerActions:
    @staticmethod
    async def restart_service(service: str, platform: str) -> str:
        cmds = {
            "linux": ["systemctl", "restart", service],
            "android": ["adb", "shell", "am", "force-stop", service],
            "macos": ["launchctl", "stop", service],
            "windows": ["powershell", "Restart-Service", service],
        }
        cmd = cmds.get(platform, [])
        if cmd:
            proc = await asyncio.create_subprocess_exec(*cmd)
            await proc.wait()
            return f"Restarted {service} on {platform}"
        return f"No command for {platform}"
    
    @staticmethod
    async def rollback_package(package: str, version: str, platform: str) -> str:
        cmds = {
            "linux": ["apt", "install", "-y", f"{package}={version}"],
            "macos": ["brew", "install", f"{package}@{version}"],
        }
        cmd = cmds.get(platform, [])
        if cmd:
            proc = await asyncio.create_subprocess_exec(*cmd)
            await proc.wait()
            return f"Rolled back {package} to {version} on {platform}"
        return f"No rollback command for {platform}"
    
    @staticmethod
    async def block_ip(ip: str, platform: str) -> str:
        """IP adresini bloklar."""
        # Yeni FirewallTool'u kullan (simüle edilmiş)
        from titan.tools.firewall import FirewallTool
        fw = FirewallTool(platform=platform)
        result = await fw.block_ip(ip)
        return f"IP {ip} blocked. Result: {result['success']}"