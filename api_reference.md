
---

## `docs/api_reference.md`

```markdown
# TITAN V4 API Referansı

## Gateway (9000)
- `GET /health` - Tüm servislerin sağlık durumu
- `POST /auth/login` - JWT token al
- `GET /api/{service}/*` - Servislere proxy

## Operator (9001)
- `GET /health` - Sağlık kontrolü
- `WS /ws` - Gerçek zamanlı log akışı

## Programmer (9002)
- `POST /api/fix` - Hata düzeltme isteği
- `POST /api/generate` - Kod üretme
- `POST /api/review` - Kod inceleme

## Researcher (9003)
- `POST /api/hypothesize` - Hipotez oluştur
- `GET /api/discoveries` - Keşifleri listele

## Companion (9004)
- `POST /api/chat` - Sohbet
- `GET /api/relationship` - İlişki durumu