# Flask Bitki Öneri Sistemi 🌿

Bu proje, kullanıcıdan alınan bütçe, cephe, sulama sıklığı, çiçek durumu, koku ve boyut gibi kriterlere göre en uygun ev bitkisini öneren bir Flask tabanlı web uygulamasıdır.

## 🔧 Özellikler
- CSV veri kümesine dayalı öneri sistemi
- Kriter bazlı puanlama ile en uygun bitki seçimi
- Graphviz ile karar ağacı çizimi
- Blog linki önerisi (otomatik kontrol)
- Bitki görseli eşleştirme (dosya sistemi üzerinden)

## 📁 Proje Dosyaları
- `oneri.py`: Ana Flask uygulaması
- `templates/index2.html`: Form ve sonuç sayfası
- `static/images/`: Bitki görselleri
- `evde_bakilabilir_bitkiler_dataset_guncel.csv`: Veri kümesi

## 🚀 Çalıştırmak için
```bash
pip install flask pandas graphviz unidecode requests
python oneri.py
