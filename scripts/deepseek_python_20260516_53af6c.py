#!/usr/bin/env python3
"""Ollama bağlantı testi."""

import asyncio
from titan.tools.llm import OllamaClient, LLMGateway

async def test_ollama():
    print("🦙 Ollama Bağlantı Testi")
    print("=" * 40)
    
    client = OllamaClient()
    
    # 1. Ollama çalışıyor mu?
    print("\n1. Ollama sunucu kontrolü...")
    if await client.is_running():
        print("   ✅ Ollama çalışıyor!")
    else:
        print("   ❌ Ollama çalışmıyor! 'ollama serve' komutunu çalıştırın.")
        return
    
    # 2. Mevcut modeller
    print("\n2. Mevcut modeller...")
    models = await client.list_models()
    for model in models:
        print(f"   - {model}")
    
    if not models:
        print("   ⚠️ Hiç model yok! Önce 'ollama pull llama3.2:3b' çalıştırın.")
        return
    
    # 3. Test mesajı
    print("\n3. Test mesajı gönderiliyor...")
    result = await client.generate(
        prompt="Merhaba! Kendini tanıtır mısın?",
        system="Sen yardımsever bir yapay zekasın. Kısa ve samimi cevap ver.",
        temperature=0.7
    )
    
    print(f"   Yanıt: {result.get('response', 'Yanıt yok')}")
    print(f"   Süre: {result.get('total_duration', 0) / 1e9:.2f} saniye")
    print(f"   Token sayısı: {result.get('eval_count', 0)}")
    
    print("\n✅ Test tamamlandı!")

async def test_llm_gateway():
    print("\n" + "=" * 40)
    print("🔄 LLM Gateway Testi")
    print("=" * 40)
    
    config = {
        "provider": "ollama",
        "ollama_url": "http://localhost:11434",
        "ollama_model": "llama3.2:3b"
    }
    
    gateway = LLMGateway(config)
    
    print("\n1. Gateway durumu...")
    print(f"   Provider: {gateway.provider}")
    print(f"   Ollama: {'Aktif' if await gateway.is_ollama_running() else 'Pasif'}")
    
    print("\n2. Sohbet testi...")
    messages = [
        {"role": "system", "content": "Sen TITAN V4'sün. Kısa ve net cevap ver."},
        {"role": "user", "content": "TITAN V4 nedir? Tek cümleyle açıkla."}
    ]
    
    response = await gateway.chat(messages)
    print(f"   Yanıt: {response}")
    
    print("\n✅ LLM Gateway testi tamamlandı!")

if __name__ == "__main__":
    asyncio.run(test_ollama())
    asyncio.run(test_llm_gateway())