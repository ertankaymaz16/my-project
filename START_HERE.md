# 🚀 BURADAN BAŞLAYIN!

## 🎯 Hollanda Vize Randevu Otomasyonu

Hoş geldiniz! Bu bot, VFS Global Hollanda vize sistemi için otomatik randevu alma aracıdır.

---

## ⚡ HIZLI BAŞLANGIÇ (5 Dakika)

### 1️⃣ Kurulum
```bash
./setup.sh
```

### 2️⃣ Konfigürasyon
```bash
cp config.json.example config.json
nano config.json
```

**Doldurmanız gerekenler:**
- VFS Global email/şifre
- Gmail App Password
- Telegram Bot Token
- Başvuran bilgileri (2 kişi)
- Kart bilgileri

### 3️⃣ Çalıştır
```bash
python main.py
```

---

## 📚 DOKÜMANTASYON

### Yeni Başlayanlar İçin
1. **[QUICKSTART.md](QUICKSTART.md)** ← BURADAN BAŞLAYIN
   - 5 dakikada kurulum
   - Adım adım rehber
   - Telegram bot oluşturma
   - Gmail App Password

### Detaylı Bilgi
2. **[README.md](README.md)**
   - Tüm özellikler
   - Detaylı konfigürasyon
   - Troubleshooting
   - Kullanım senaryoları

### Geliştiriciler İçin
3. **[ARCHITECTURE.md](ARCHITECTURE.md)**
   - Teknik mimari
   - Modül detayları
   - Veri akışı
   - Performans optimizasyonları

### Proje Bilgileri
4. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**
   - Proje özeti
   - İstatistikler
   - Kod metrikleri

5. **[DELIVERY_REPORT.md](DELIVERY_REPORT.md)**
   - Teslimat raporu
   - Tamamlanan özellikler
   - Test durumu

---

## 🎯 NE YAPAR?

### FAZ 1: Otomatik Giriş
- VFS Global'e giriş yapar
- Email'den OTP kodunu otomatik çeker
- Oturumu başlatır

### FAZ 2: Randevu Tarama
- Her 10 dakikada bir kontrol eder
- Bursa + Turistik Vize + 2 Kişi
- Randevu bulunca Telegram'dan bildirir

### FAZ 3: Hızlı Rezervasyon
- Milisaniyeler içinde form doldurur
- 2 kişinin bilgilerini girer
- Rezervasyonu tamamlar

### FAZ 4: Ödeme
- Kart bilgilerini girer
- 3D Secure SMS kodunu Telegram'dan alır
- Ödemeyi tamamlar

---

## 📱 TELEGRAM KULLANIMI

Bot çalışırken Telegram'dan:
1. ✅ Durum güncellemeleri alırsınız
2. 🎯 Randevu bulundu bildirimi
3. 💳 SMS kodu istenir (3D Secure için)
4. 🎉 Ödeme tamamlandı bildirimi

**SMS Kodu Gönderme:**
Bot `💳 SMS KODUNU GİRİN:` dediğinde, bankanızdan gelen SMS kodunu Telegram'a yazın.

---

## ⚙️ ÖNEMLİ AYARLAR

### İlk Test İçin
```json
{
  "settings": {
    "polling_interval_minutes": 5,
    "headless": false,  // Tarayıcıyı görün
    "screenshot_on_error": true
  }
}
```

### 7/24 Çalışma İçin
```json
{
  "settings": {
    "polling_interval_minutes": 10,
    "headless": true,  // Arka planda
    "screenshot_on_error": true
  }
}
```

---

## 🆘 SORUN MU YAŞIYORSUNUZ?

### Hızlı Çözümler

**"Config file not found"**
```bash
cp config.json.example config.json
```

**"Email connection failed"**
- Gmail App Password kullanın (normal şifre değil!)
- 2 Adımlı Doğrulama aktif olmalı

**"Telegram bot failed"**
- Bot token doğru mu?
- Bot'u Telegram'da `/start` ile başlattınız mı?

**"Login failed"**
- VFS credentials doğru mu?
- Headless mode'u kapatın: `"headless": false`

### Detaylı Yardım
- [README.md](README.md) → Troubleshooting bölümü
- Log dosyaları: `logs/VisaBot_*.log`
- Screenshot'lar: `logs/*.png`

---

## 📊 PROJE YAPISI

```
visa-bot/
├── START_HERE.md          ← Bu dosya
├── QUICKSTART.md          ← Hızlı başlangıç
├── README.md              ← Detaylı kılavuz
├── ARCHITECTURE.md        ← Teknik dokümantasyon
├── main.py                ← Ana program
├── config.json.example    ← Örnek konfigürasyon
├── setup.sh               ← Kurulum scripti
├── requirements.txt       ← Python bağımlılıkları
├── modules/               ← Bot modülleri
│   ├── browser.py
│   ├── auth.py
│   ├── mail_handler.py
│   ├── appointment.py
│   ├── payment.py
│   └── telegram_bot.py
└── utils/                 ← Yardımcı araçlar
    ├── logger.py
    └── stealth.py
```

---

## ✅ KONTROL LİSTESİ

Başlamadan önce:
- [ ] Python 3.8+ yüklü
- [ ] VFS Global hesabı var
- [ ] Gmail hesabı var (App Password ile)
- [ ] Telegram hesabı var
- [ ] Bot token aldım
- [ ] Chat ID öğrendim
- [ ] config.json doldurdum
- [ ] setup.sh çalıştırdım

---

## 🎓 SONRAKİ ADIMLAR

1. ✅ [QUICKSTART.md](QUICKSTART.md) okuyun (5 dakika)
2. ⚙️ config.json dosyasını doldurun
3. 🚀 `python main.py` ile başlatın
4. 📱 Telegram'dan takip edin
5. 🎉 Randevunuzu alın!

---

## 💡 PRO İPUÇLARI

### Screen ile 7/24 Çalıştırma
```bash
screen -S visa-bot
python main.py
# Ctrl+A+D ile detach
# screen -r visa-bot ile geri dön
```

### Log Takibi
```bash
tail -f logs/VisaBot_*.log
```

### Hata Logları
```bash
grep ERROR logs/VisaBot_*.log
```

---

## 🔒 GÜVENLİK

- ⚠️ `config.json` dosyasını ASLA paylaşmayın
- ⚠️ Kart bilgilerinizi güvenli tutun
- ⚠️ Bot'u sadece güvendiğiniz ortamlarda çalıştırın
- ⚠️ Log dosyalarında hassas bilgi olabilir

---

## 📞 YARDIM

1. **Dokümantasyon:** [QUICKSTART.md](QUICKSTART.md), [README.md](README.md)
2. **Log Dosyaları:** `logs/VisaBot_*.log`
3. **Screenshot'lar:** `logs/*.png`
4. **Troubleshooting:** README.md → Troubleshooting bölümü

---

## 🎉 BAŞARILAR!

Bot hazır ve çalışır durumda. Sadece konfigürasyonu doldurun ve başlatın!

**Randevunuz yakında! 🇳🇱**

---

**Hızlı Başlangıç:** [QUICKSTART.md](QUICKSTART.md)  
**Detaylı Kılavuz:** [README.md](README.md)  
**Teknik Dokümantasyon:** [ARCHITECTURE.md](ARCHITECTURE.md)
