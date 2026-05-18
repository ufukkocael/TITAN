#!/usr/bin/env python3
# start.py - TITAN V4 Ana Başlatma Betiği

import subprocess
import time
import sys
import os
import signal
import socket # Eklenen

# Servis tanımları
services = [
    {"name": "API Gateway", "path": "api/gateway/main.py", "port": 9000},
    {"name": "Orchestrator", "path": "services/orchestrator/main.py", "port": 9005},
    {"name": "Cloud Mock", "path": "services/cloud_mock/main.py", "port": 9100},
    {"name": "Operator", "path": "services/operator/main.py", "port": 9001},
    {"name": "Programmer", "path": "services/programmer/main.py", "port": 9002},
    {"name": "Researcher", "path": "services/researcher/main.py", "port": 9003},
    {"name": "Companion", "path": "services/companion/main.py", "port": 9004},
    {"name": "Desktop UI", "path": "dashboard/launcher.py", "port": 0},
]

processes = []


def print_banner():
    print("""
    \033[96m
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║   ████████╗██╗████████╗ █████╗ ███╗   ██╗    ██╗   ██╗███████╗   ║
    ║   ╚══██╔══╝██║╚══██╔══╝██╔══██╗████╗  ██║    ██║   ██║██╔════╝   ║
    ║      ██║   ██║   ██║   ███████║██╔██╗ ██║    ██║   ██║█████╗     ║
    ║      ██║   ██║   ██║   ██╔══██║██║╚██╗██║    ╚██╗ ██╔╝██╔══╝     ║
    ║      ██║   ██║   ██║   ██║  ██║██║ ╚████║     ╚████╔╝ ███████╗   ║
    ║      ╚═╝   ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝      ╚═══╝  ╚══════╝   ║
    ║                                                                  ║
    ║                     V E R S I O N   4 . 0                        ║
    ║              Autonomous AI Operations System                     ║
    ║                    by U.KOCAEL                                   ║
    ╚══════════════════════════════════════════════════════════════════╝
    \033[0m
    """)


def start_services():
    print("🚀 [SYSTEM] TITAN V4 Bilişsel Platformu Başlatılıyor...")
    time.sleep(1)
    
    # PYTHONPATH ayarla
    env = os.environ.copy()
    titan_core_path = os.path.abspath("titan-core")
    env["PYTHONPATH"] = f"{titan_core_path}{os.pathsep}{env.get('PYTHONPATH', '')}"
    
    for service in services:
        print(f"📦 {service['name']} başlatılıyor (Port: {service['port']})...")
        service_dir = os.path.dirname(service["path"])
        service_file = os.path.basename(service["path"])
        
        s_env = env.copy()
        s_env["PYTHONPATH"] = f"{os.path.abspath(service_dir)}{os.pathsep}{s_env.get('PYTHONPATH', '')}"
        s_env["TITAN_CENTRAL_URL"] = "http://localhost:9100"
        
        try:
            p = subprocess.Popen(
                [sys.executable, service_file],
                cwd=os.path.abspath(service_dir),
                env=s_env
            )
            processes.append((service["name"], p))
            time.sleep(2)
            
            if p.poll() is not None:
                print(f"❌ {service['name']} hemen kapandı! (Hata kodu: {p.returncode})")
        except Exception as e:
            print(f"❌ {service['name']} başlatılamadı: {e}")

    print("\n✅ Servisler başlatıldı.\n")
    print("📊 Servis durumunu kontrol etmek için:")
    print("   curl http://localhost:9000/health")
    print("")
    print("🛑 Durdurmak için: Ctrl+C")
    print("")


def signal_handler(sig, frame):
    print("\n\n🛑 TITAN V4 kapatılıyor...")
    for name, p in processes:
        print(f"   Durduruluyor: {name}")
        p.terminate()
        try:
            p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            p.kill()
    print("✅ Tüm servisler durduruldu.")
    sys.exit(0)


def cleanup_ports():
    """Önceki oturumlardan kalan süreçleri temizler."""
    import socket
    print("🧹 Eski süreçler temizleniyor...")
    ports = [9000, 9001, 9002, 9003, 9004, 9005, 9100]
    for port in ports:
        if sys.platform == 'win32':
            # Windows için portu kullanan PID'yi bul ve öldür
            try:
                cmd = f"netstat -ano | findstr :{port}"
                output = subprocess.check_output(cmd, shell=True).decode()
                for line in output.splitlines():
                    if "LISTENING" in line:
                        pid = line.strip().split()[-1]
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
            except:
                pass
    time.sleep(1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    print_banner()
    cleanup_ports()
    start_services()
    
    try:
        while True:
            time.sleep(1)
            # Çöken servisleri kontrol et
            for name, p in list(processes):
                if p.poll() is not None:
                    print(f"⚠️ {name} durdu! Yeniden başlatılıyor...")
                    processes.remove((name, p))
                    # Yeniden başlatma mantığı buraya eklenebilir
    except KeyboardInterrupt:
        signal_handler(None, None)