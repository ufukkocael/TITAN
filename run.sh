# Tüm sistemi tek komutla başlat
docker-compose up -d

# Gateway sağlık kontrolü
curl http://localhost:9000/health

# Gateway üzerinden Operator'a istek
curl http://localhost:9000/api/operator/health

# Gateway üzerinden Programmer'a istek
curl -X POST http://localhost:9000/api/programmer/api/fix \
  -H "Content-Type: application/json" \
  -d '{"error_message": "memory leak detected"}'

# Gateway üzerinden Researcher'a istek
curl -X POST http://localhost:9000/api/researcher/api/hypothesize \
  -H "Content-Type: application/json" \
  -d '{"observation": "CPU usage spike"}'

# Gateway üzerinden Companion'a istek
curl -X POST http://localhost:9000/api/companion/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Merhaba TITAN"}'