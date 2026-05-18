# TITAN V4 - Dağıtık Bilişsel Sistem Mimarisi

**Geliştirici:** U.KOCAEL

TITAN V4, otonom yönetim, kod üretimi, bilimsel araştırma ve kullanıcı etkileşimi özelliklerine sahip çok katmanlı bir yapay zeka platformudur.

## Son Yapılan İyileştirmeler ve Düzeltmeler

Sistem genelindeki eksik ve hatalı kodlar üzerinde aşağıdaki kritik güncellemeler yapılmıştır:

1.  **Orkestratör Mantığı Tamamlandı (`orchestrator.py`):**
    *   Kullanıcı geri bildirimlerine dayalı "güven skoru" (trust score) güncelleme mekanizması eklendi.
    *   İlişki durumu güncellemeleri için olay işleyici (handler) implemente edildi.
    *   Bellek bakım döngüsü (memory maintenance) aktif hale getirildi; düşük öncelikli eski anıların temizlenmesi sağlandı.

2.  **API Gateway Güvenlik ve Performans İyileştirmeleri (`api/main.py`):**
    *   Hardcoded şifreleme mantığı çevre değişkenleri (environment variables) ile desteklendi.
    *   Sistem çalışma süresi (uptime) hesaplamasındaki mantıksal hata düzeltildi.
    *   `login` fonksiyonundaki parametre alımı FastAPI standartlarına uygun hale getirildi (`Form` desteği).

3.  **Bilişsel Önceliklendirme Motoru Düzeltildi (`priority_manager.py`):**
    *   `effective_priority` hesaplamasına görev öncelik seviyesi (Priority Enum) dahil edilerek kritik görevlerin öne çıkması sağlandı.

4.  **Hata Yönetimi ve Stabilite:**
    *   `bridge.py` dosyasında ChromaDB sorgu sonuçlarının boş dönmesi durumunda oluşabilecek `IndexError` hatası giderildi.
    *   `patch_generator.py` dosyasındaki tanımsız değişken hatası düzeltildi.
    *   WebSocket mesaj iletimindeki sessiz hata oluşumları engellenerek loglama eklendi.

## Modüller

- **Core (titan-core):** Tesseract 4D, Bilişsel Scheduler, Mesaj Bus.
- **Operator (9001):** Anomali tespiti ve otomatik iyileştirme.
- **Programmer (9002):** Otomatik kod üretimi ve yama yönetimi.
- **Researcher (9003):** Hipotez testi ve beceri damıtma.
- **Companion (9004):** Kişiselleştirilmiş kullanıcı deneyimi ve hafıza.

## Başlatma

```bash
# Bağımlılıkları yükleyin
pip install -e titan-core
pip install -r requirements.txt

# Sistemi başlatın
python start.py
```
