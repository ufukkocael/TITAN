#!/bin/bash
echo "TITAN V4 - Kurulum Betiği"
echo "========================"

# titan-core kurulumu
echo "1. titan-core kuruluyor..."
cd titan-core
pip install -e .
cd ..

# Servis bağımlılıkları
echo "2. Servis bağımlılıkları kuruluyor..."
pip install -r services/operator/requirements.txt
pip install -r services/programmer/requirements.txt
pip install -r services/researcher/requirements.txt
pip install -r services/companion/requirements.txt
pip install -r api/gateway/requirements.txt

echo "✅ Kurulum tamamlandı."
echo "Başlatmak için: python start.py"