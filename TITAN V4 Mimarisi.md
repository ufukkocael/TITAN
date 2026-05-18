# TITAN V4 Mimarisi

## Genel Bakış
TITAN V4, dağıtık bilişsel sistem mimarisine sahip, kendi kendini yöneten bir yapay zeka platformudur.

## Katmanlar
1. **Core**: Tesseract 4D hiper-uzay, SpiralMemory, InertiaCircle
2. **Memory**: WisdomVault (ChromaDB), Episodic, Semantic, Working
3. **Brain**: Reasoning, WorldModel, Identity, Evaluator
4. **Executive**: Priority, Attention, Resource, MetaGoal
5. **Integration**: MessageBus, Orchestrator

## Servisler
- Operator (9001): İzleme, anomali tespiti, otomatik iyileştirme
- Programmer (9002): Kod üretimi, yama, test
- Researcher (9003): Hipotez, deney, öz-iyileştirme
- Companion (9004): Sohbet, ses, kişisel hafıza
- API Gateway (9000): Yönlendirme, auth, rate limit

## Başlatma
```bash
pip install -e titan-core
python start.py