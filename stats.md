# Statistics Dashboard - Proje Özeti ve Teknik Bilgiler

Bu dosya, Sedna Statistics Dashboard projesinin çalışma mantığını ve erişim bilgilerini içerir.

## 1. Erişim Bilgileri
- **Yerel Adres:** `http://localhost:8085`
- **Ağ Adresi (IP):** `http://192.168.0.128:8085`
- **Manuel Güncelleme:** Dashboard'un altındaki "GÜNCELLE" butonu ile veriler anında yenilenebilir.

## 2. Veri Mantığı (Data Logic)

### A. Geceleme ve Kişi (Nights / Pax)
- **Kapsam:** 1 Mayıs'tan bugüne kadar olan aralık.
- **Statü:** Sadece `Status = 1` (Kesinleşmiş/Forecast) rezervasyonlar sayılır.
- **Kişi Sayısı:** Otel +16 konseptinde olduğu için `Pax + Childs` (Yetişkin + Çocuk) toplamı doğrudan yetişkin sayısını yansıtacak şekilde ayarlanmıştır.

### B. Oda Doluluk Oranı (Season Pace)
- **Kapsam:** 1 Mayıs - 30 Ekim (Tüm Sezon).
- **Mantık:** Sezonun toplam kapasitesinin ne kadarının "bugün itibariyle" satıldığını gösterir.
- **Kıyaslama:** 2024 ve 2025 yılları da tam olarak "bugünkü tarihte o yıl ne durumdaydık" (Season Pace) mantığıyla filtrelenerek elma-elma kıyaslaması yapılır.

### C. Gelirler (Revenue)
- **Kaynak:** Sedna `ManagerReport` prosedürü.
- **Vergi Durumu:** Gösterilen rakamlar KDV ve vergilerden arındırılmış **NET** rakamlardır.
- **Tip:** Tahakkuk (Accrual) bazlı gelirdir (Kasa raporu/Nakit akışı değildir).

## 3. Önemli Dosyalar
- `stats_dashboard.py`: Sunucu ve arayüz mantığı.
- `queries.py`: SQL sorguları ve veri çekme mantığı.
- `templates/index.html`: Dashboard tasarımı.
- `.env`: Veritabanı bağlantı ve port ayarları.

## 4. Port Bilgisi
Proje, ağdaki diğer projelerle (8081, 5080) çakışmaması ve VPN üzerinden erişim kolaylığı için **8085** portuna taşınmıştır.
