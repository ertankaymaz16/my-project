# 🇳🇱 Hollanda Vize Randevu Otomasyonu (RPA Bot)

Hollanda Vize Sistemi (VFS Global/Konsolosluk) için geliştirilmiş, uçtan uca otomatik randevu alma botu.

## 🎯 Özellikler

### ✅ Tam Otomatik İşlem Akışı
- **FAZ 1**: Güvenli giriş ve OTP doğrulama (Email entegrasyonu)
- **FAZ 2**: Akıllı randevu tarama (10 dakikalık interval, anti-bot koruması)
- **FAZ 3**: Hızlı rezervasyon ve form doldurma (milisaniyeler içinde)
- **FAZ 4**: Ödeme ve 3D Secure (Human-in-the-loop Telegram entegrasyonu)

### 🛡️ Anti-Detection (Stealth Mode)
- Playwright ile gerçek tarayıcı parmak izi
- Cloudflare ve WAF bypass
- İnsan benzeri davranış simülasyonu
- Random mouse movements ve delays
- Gerçekçi User-Agent ve viewport

### 📱 Telegram Entegrasyonu
- Anlık bildirimler
- Randevu bulundu uyarısı
- 3D Secure SMS kodu girişi
- Hata bildirimleri ve screenshot'lar

### 📧 Email OTP Otomasyonu
- Gmail/Outlook IMAP entegrasyonu
- Otomatik OTP kodu çekme
- Regex ile akıllı kod tespiti

### 🔄 Hata Yönetimi
- Otomatik retry mekanizması
- Session yönetimi ve cookie persistence
- Comprehensive logging
- Screenshot on error
- Graceful shutdown

## 📋 Gereksinimler

- Python 3.8+
- Gmail/Outlook hesabı (App Password ile)
- Telegram Bot Token
- VFS Global hesabı

## 🚀 Kurulum

### 1. Depoyu Klonlayın
```bash
git clone <repo-url>
cd visa-bot
```

### 2. Python Bağımlılıklarını Yükleyin
```bash
pip install -r requirements.txt
```

### 3. Playwright Tarayıcılarını Yükleyin
```bash
playwright install chromium
```

### 4. Konfigürasyon Dosyasını Oluşturun
```bash
cp config.json.example config.json
```

### 5. `config.json` Dosyasını Düzenleyin

```json
{
  "vfs_credentials": {
    "email": "vfs_hesabiniz@example.com",
    "password": "vfs_sifreniz"
  },
  "email_config": {
    "provider": "gmail",
    "email": "gmail_hesabiniz@gmail.com",
    "password": "gmail_app_password",
    "imap_server": "imap.gmail.com",
    "imap_port": 993
  },
  "telegram": {
    "bot_token": "TELEGRAM_BOT_TOKEN",
    "chat_id": "TELEGRAM_CHAT_ID"
  },
  "appointment_criteria": {
    "location": "Bursa",
    "visa_type": "Tourist",
    "number_of_people": 2
  },
  "applicants": [
    {
      "first_name": "Ahmet",
      "last_name": "Yılmaz",
      "tc_number": "12345678901",
      "passport_number": "U12345678",
      "birth_date": "01/01/1990",
      "phone": "+905551234567",
      "email": "ahmet@example.com"
    },
    {
      "first_name": "Ayşe",
      "last_name": "Yılmaz",
      "tc_number": "98765432109",
      "passport_number": "U98765432",
      "birth_date": "15/05/1992",
      "phone": "+905559876543",
      "email": "ayse@example.com"
    }
  ],
  "payment": {
    "card_number": "1234567890123456",
    "card_holder": "AHMET YILMAZ",
    "expiry_month": "12",
    "expiry_year": "2025",
    "cvv": "123"
  },
  "settings": {
    "polling_interval_minutes": 10,
    "headless": true,
    "screenshot_on_error": true,
    "max_retries": 3,
    "random_delay_min": 8,
    "random_delay_max": 12
  }
}
```

## 🔧 Konfigürasyon Detayları

### Gmail App Password Oluşturma
1. Google Hesabınıza gidin
2. Güvenlik → 2 Adımlı Doğrulama → Uygulama Şifreleri
3. "Mail" için yeni bir uygulama şifresi oluşturun
4. Oluşturulan şifreyi `email_config.password` alanına yapıştırın

### Telegram Bot Oluşturma
1. Telegram'da [@BotFather](https://t.me/botfather) ile konuşun
2. `/newbot` komutu ile yeni bot oluşturun
3. Bot token'ı alın ve `telegram.bot_token` alanına yapıştırın
4. Chat ID'nizi öğrenmek için [@userinfobot](https://t.me/userinfobot) kullanın
5. Chat ID'yi `telegram.chat_id` alanına yapıştırın

### VFS Global URL'lerini Güncelleme
Bot, VFS Global'in Hollanda vize sistemi için yazılmıştır. Gerçek URL'leri güncellemek için:

1. `modules/auth.py` dosyasını açın
2. `LOGIN_URL` ve `DASHBOARD_URL` değişkenlerini güncelleyin

```python
LOGIN_URL = "https://visa.vfsglobal.com/tur/tr/nld/login"
DASHBOARD_URL = "https://visa.vfsglobal.com/tur/tr/nld/dashboard"
```

3. `modules/appointment.py` dosyasını açın
4. `APPOINTMENT_URL` değişkenini güncelleyin

```python
APPOINTMENT_URL = "https://visa.vfsglobal.com/tur/tr/nld/book-an-appointment"
```

## ▶️ Çalıştırma

```bash
python main.py
```

### Headless Mode (Arka Planda)
```bash
# config.json içinde "headless": true olarak ayarlayın
python main.py
```

### Debug Mode (Tarayıcı Görünür)
```bash
# config.json içinde "headless": false olarak ayarlayın
python main.py
```

## 📊 İşleyiş Akışı

```
┌─────────────────────────────────────────────────────────────┐
│                    FAZ 1: GİRİŞ & OTP                       │
├─────────────────────────────────────────────────────────────┤
│ 1. VFS Global'e giriş yap                                   │
│ 2. Email'den OTP kodunu otomatik çek                        │
│ 3. OTP'yi gir ve oturumu başlat                             │
│ 4. Cookie'leri kaydet                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              FAZ 2: RANDEVU TARAMA (POLLING)                │
├─────────────────────────────────────────────────────────────┤
│ 1. Her 10 dakikada bir kontrol et                          │
│ 2. Bursa + Turistik Vize + 2 Kişi filtresi uygula          │
│ 3. Randevu YOKSA → Random delay (8-12 dk)                  │
│ 4. Randevu VARSA → Telegram bildirimi + FAZ 3'e geç        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           FAZ 3: REZERVASYON & FORM DOLDURMA                │
├─────────────────────────────────────────────────────────────┤
│ 1. Telegram: "🎯 RANDEVU BULUNDU!"                          │
│ 2. Randevu slot'una tıkla                                   │
│ 3. 2 kişinin bilgilerini ışık hızında doldur               │
│ 4. Rezervasyonu onayla                                      │
│ 5. Telegram: "✅ REZERVASYON BAŞARILI!"                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         FAZ 4: ÖDEME & 3D SECURE (HUMAN-IN-LOOP)            │
├─────────────────────────────────────────────────────────────┤
│ 1. Kart bilgilerini doldur                                  │
│ 2. "Öde" butonuna bas                                       │
│ 3. 3D Secure ekranı geldiğinde BOT BEKLE                    │
│ 4. Telegram: "💳 SMS KODUNU GİRİN:"                         │
│ 5. Kullanıcı Telegram'dan SMS kodunu gönderir               │
│ 6. Bot kodu alıp banka sayfasına girer                      │
│ 7. Ödemeyi tamamla                                          │
│ 8. Telegram: "🎉 ÖDEME TAMAMLANDI!"                         │
└─────────────────────────────────────────────────────────────┘
```

## 🎮 Telegram Komutları

Bot çalışırken Telegram üzerinden şu mesajları alırsınız:

- `🤖 Vize Randevu Botu başlatıldı!` - Bot başladı
- `🔍 Tarama devam ediyor... (Deneme #10)` - Her 10 denemede bir durum
- `🎯 RANDEVU BULUNDU!` - Randevu bulundu
- `✅ REZERVASYON BAŞARILI!` - Rezervasyon tamamlandı
- `💳 3D SECURE SMS KODUNU GİRİN:` - SMS kodu bekleniyor
- `🎉 ÖDEME TAMAMLANDI!` - İşlem başarılı
- `❌ HATA OLUŞTU` - Hata durumunda

### SMS Kodu Gönderme
Bot `💳 3D SECURE SMS KODUNU GİRİN:` mesajını gönderdiğinde:
1. Bankanızdan gelen SMS'i kontrol edin
2. Sadece kodu (örn: `123456`) Telegram'a yazın
3. Bot otomatik olarak kodu alıp işleme devam eder

## 📁 Proje Yapısı

```
visa-bot/
├── main.py                 # Ana orchestrator
├── config.json             # Konfigürasyon (GİZLİ - .gitignore'da)
├── config.json.example     # Örnek konfigürasyon
├── requirements.txt        # Python bağımlılıkları
├── README.md              # Bu dosya
├── modules/
│   ├── __init__.py
│   ├── browser.py         # Playwright browser yönetimi
│   ├── auth.py            # Giriş ve OTP yönetimi
│   ├── mail_handler.py    # Email OTP çekme
│   ├── appointment.py     # Randevu tarama ve rezervasyon
│   ├── payment.py         # Ödeme ve 3D Secure
│   └── telegram_bot.py    # Telegram entegrasyonu
├── utils/
│   ├── __init__.py
│   ├── logger.py          # Loglama sistemi
│   └── stealth.py         # Anti-detection helpers
└── logs/                  # Log dosyaları
    └── VisaBot_YYYYMMDD.log
```

## 🔍 Loglama

Bot, detaylı logları hem konsola hem de dosyaya yazar:

- **Konsol**: Renkli, özet loglar (INFO seviyesi)
- **Dosya**: Detaylı loglar (DEBUG seviyesi) - `logs/VisaBot_YYYYMMDD.log`

Log seviyeleri:
- 🔵 DEBUG: Detaylı debug bilgileri
- 🟢 INFO: Genel bilgilendirme
- 🟡 WARNING: Uyarılar
- 🔴 ERROR: Hatalar
- ⚫ CRITICAL: Kritik hatalar

## 🛠️ Troubleshooting

### Bot giriş yapamıyor
- VFS credentials'ları kontrol edin
- Email OTP ayarlarını kontrol edin
- `headless: false` yaparak tarayıcıyı görün

### OTP kodu gelmiyor
- Gmail App Password'ü doğru girdiğinizden emin olun
- IMAP ayarlarını kontrol edin
- Email'inizde "VFS" veya "visa" içeren yeni bir mail olup olmadığını kontrol edin

### Telegram bildirimleri gelmiyor
- Bot token'ı doğru mu?
- Chat ID doğru mu?
- Bot'u Telegram'da başlattınız mı? (`/start` komutu)

### Randevu bulunamıyor
- Filtreleri kontrol edin (Bursa, Tourist, 2 kişi)
- VFS sitesinde manuel olarak randevu var mı kontrol edin
- Polling interval'i azaltın (dikkatli olun, ban yiyebilirsiniz)

### 3D Secure çalışmıyor
- SMS kodunu doğru girdiğinizden emin olun
- Sadece rakamları gönderin (boşluk veya harf olmadan)
- Timeout süresi 5 dakikadır

## ⚠️ Önemli Notlar

### Güvenlik
- `config.json` dosyasını **ASLA** paylaşmayın veya commit etmeyin
- Kart bilgilerinizi güvenli tutun
- Bot'u sadece güvendiğiniz ortamlarda çalıştırın

### Yasal Uyarı
- Bu bot, VFS Global'in kullanım şartlarını ihlal edebilir
- Kullanımdan doğacak sorumluluk size aittir
- Sadece eğitim amaçlı kullanın

### Rate Limiting
- Çok sık tarama yapmayın (ban riski)
- Default 10 dakikalık interval önerilir
- Random delay kullanın

### Anti-Bot Sistemleri
- VFS Global, Cloudflare veya benzeri korumalar kullanabilir
- Bot, stealth mode ile çalışır ancak %100 garanti değildir
- Gerekirse CAPTCHA manuel çözülmelidir

## 🔄 Güncelleme

VFS Global sitesi değiştiğinde, selector'ları güncellemeniz gerekebilir:

1. `modules/auth.py` - Login selectors
2. `modules/appointment.py` - Appointment selectors
3. `modules/payment.py` - Payment selectors

Chrome DevTools ile element selector'larını bulabilirsiniz.

## 📞 Destek

Sorun yaşarsanız:
1. Log dosyalarını kontrol edin
2. Screenshot'ları inceleyin (`logs/` klasörü)
3. `headless: false` yaparak tarayıcıyı görün
4. Issue açın (kişisel bilgilerinizi paylaşmayın!)

## 📜 Lisans

Bu proje eğitim amaçlıdır. Ticari kullanım yasaktır.

## 🙏 Teşekkürler

- Playwright ekibine
- Python Telegram Bot kütüphanesi geliştiricilerine
- Açık kaynak topluluğuna

---

**⚡ Hızlı, Güvenli, Otomatik - Randevunuz Bizden! 🇳🇱**
