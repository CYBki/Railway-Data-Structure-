# Ankara Metro Veri Yapısı

Bu deneysel proje, Ankara metro hattını çalışan bir veri yapısı olarak modellemeyi amaçlar. 
İstasyonlar veri düğümlerine, hatlar ise bu düğümler arasındaki bağlantılara karşılık gelir. 
Ana hatlar, dallar, ekspres geçişler ve halkalar gibi birden fazla bileşeni destekler.

## Özellikler
- **Çoklu hat türleri:** ana, dal, ekspres ve halka
- **İstasyon tipleri:** normal, terminal, kavşak ve transfer
- **Rota bulma:** veri yapısında iki istasyon arasındaki en uygun yolu hesaplar
- **Ağ istatistikleri:** toplam istasyon, hat dağılımı, transfer sayısı vb.
- **ASCII görselleştirme:** ağın metin tabanlı gösterimi

## Kurulum
Python 3 yüklü bir ortam yeterlidir.

## Çalıştırma
```bash
python Subway_data_structure.py
```
Bu komut:
1. Ankara metro ağını kurar
2. Ağ yapısını ve istatistikleri ekrana basar
3. Bilkent'ten Törekent'e örnek bir rota hesaplar
4. Geleneksel liste ile performans karşılaştırması yapar

## Koddan Kullanım
```python
from Subway_data_structure import build_ankara_metro_network

network = build_ankara_metro_network()
route_ids = network.find_optimal_route("Bilkent", "Törekent")
route_names = [network.stations[s].data for s in route_ids]
print(route_names)
```

## Dosya Yapısı
- `Subway_data_structure.py`: Ağ sınıfları, Ankara metro örneği ve benchmark
- `README.md`: Proje açıklaması ve kullanım

## Lisans
Bu proje MIT Lisansı ile sunulmaktadır.
