#!/usr/bin/env python3
"""TITAN yangın tatbikatı: OpenSSL çöküş senaryosu."""
import asyncio
import random
from datetime import datetime

PLATFORMS = ["android", "linux", "windows", "macos"]

CRASH_MSGS = [
    "FATAL: OpenSSL 3.2 heap corruption at 0x7f8a...",
    "CRITICAL: OOM killer invoked for worker_12",
    "FATAL: Segmentation fault in libssl.so.3.2",
]

async def main():
    print("🔥 TITAN Yangın Tatbikatı Başlıyor...")
    print("   OpenSSL 3.2 çoklu platform çöküş senaryosu\n")
    
    for i in range(60):
        crash_mode = 15 <= i <= 35
        
        for platform in PLATFORMS:
            if crash_mode:
                msg = random.choice(CRASH_MSGS)
                sev = "FATAL"
            else:
                msg = f"INFO: {platform} normal operation"
                sev = "INFO"
            
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "platform": platform,
                "severity": sev,
                "message": msg,
            }
            print(f"   [{entry['platform']:7s}] {sev:8s} | {msg[:60]}")
            await asyncio.sleep(0.3)
        
        if i == 15:
            print("\n⚠️  KRİZ BAŞLADI!\n")
        elif i == 35:
            print("\n✅ KRİZ ÇÖZÜLDÜ!\n")
    
    print("\n🎉 Tatbikat tamamlandı.")

asyncio.run(main())