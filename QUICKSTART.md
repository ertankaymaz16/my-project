# 🚀 Hızlı Başlangıç Kılavuzu

## 5 Dakikada Kurulum

### 1️⃣ Kurulum Scriptini Çalıştır
```bash
./setup.sh
```

Bu script otomatik olarak:
- Virtual environment oluşturur
- Tüm bağımlılıkları yükler
- Playwright tarayıcılarını indirir
- config.json dosyasını oluşturur

### 2️⃣ Telegram Bot Oluştur

1. Telegram'da [@BotFather](https://t.me/botfather) ile konuş
2. `/newbot` komutunu gönder
3. Bot adı ve kullanıcı adı belirle
4. Bot token'ı kopyala (örn: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. [@userinfobot](https://t.me/userinfobot) ile chat ID'ni öğren

### 3️⃣ Gmail App Password Oluştur

1. [Google Hesap Güvenlik](https://myaccount.google.com/security) sayfasına git
2. "2 Adımlı Doğrulama" aktif olmalı
3. "Uygulama şifreleri" bölümüne git
4. "Mail" için yeni şifre oluştur
5. 16 haneli şifreyi kopyala (örn: `abcd efgh ijkl mnop`)

### 4️⃣ Config Dosyasını Düzenle

```bash
nano config.json
```

veya favori editörünüzle açın ve şu alanları doldurun:

```json
{
  "vfs_credentials": {
    "email": "vfs_hesabiniz@example.com",      // VFS Global email
    "password": "vfs_sifreniz"                  // VFS Global şifre
  },
  "email_config": {
    "email": "gmail_hesabiniz@gmail.com",       // Gmail adresiniz
    "password": "abcd efgh ijkl mnop"           // Gmail App Password (16 hane)
  },
  "telegram": {
    "bot_token": "123456789:ABCdefGHI...",      // BotFather'dan aldığınız token
    "chat_id": "123456789"                      // userinfobot'tan aldığınız ID
  },
  "applicants": [
    {
      "first_name": "Ahmet",                    // İlk başvuran adı
      "last_name": "Yılmaz",                    // İlk başvuran soyadı
      "tc_number": "12345678901",               // TC Kimlik No
      "passport_number": "U12345678",           // Pasaport No
      "birth_date": "01/01/1990",               // Doğum tarihi
      "phone": "+905551234567",                 // Telefon
      "email": "ahmet@example.com"              // Email
    },
    {
      // İkinci başvuran bilgileri...
    }
  ],
  "payment": {
    "card_number": "1234567890123456",          // Kart numarası (16 hane)
    "card_holder": "AHMET YILMAZ",              // Kart üzerindeki isim
    "expiry_month": "12",                       // Son kullanma ayı
    "expiry_year": "2025",                      // Son kullanma yılı
    "cvv": "123"                                // CVV (3 hane)
  }
}
```

### 5️⃣ Botu Çalıştır

```bash
# Virtual environment'ı aktifleştir
source venv/bin/activate

# Botu başlat
python main.py
```

## ✅ İlk Çalıştırma Kontrol Listesi

- [ ] Python 3.8+ yüklü
- [ ] setup.sh çalıştırıldı
- [ ] Telegram bot oluşturuldu ve token alındı
- [ ] Gmail App Password oluşturuldu
- [ ] config.json düzenlendi ve kaydedildi
- [ ] VFS Global hesabı var ve aktif
- [ ] Kart bilgileri doğru girildi
- [ ] Başvuran bilgileri eksiksiz

## 🎯 İlk Test

Bot başladığında şu adımları izleyin:

1. **Telegram'ı kontrol edin**: "🤖 Vize Randevu Botu başlatıldı!" mesajı gelmelidir
2. **Konsolu izleyin**: Renkli loglar akmalıdır
3. **Giriş kontrolü**: "✅ Login successful!" mesajını bekleyin
4. **Polling başlangıcı**: "🔹 [FAZ 2] Polling attempt #1" görmelisiniz

## 🐛 Hızlı Sorun Giderme

### "Config file not found"
```bash
cp config.json.example config.json
nano config.json
```

### "Failed to connect to email"
- Gmail App Password'ü kontrol edin (boşluksuz girin)
- 2 Adımlı Doğrulama aktif mi?
- IMAP erişimi açık mı? (Gmail ayarlarından)

### "Telegram bot initialization failed"
- Bot token doğru mu?
- Chat ID doğru mu?
- Bot'u Telegram'da `/start` ile başlattınız mı?

### "Login failed"
- VFS credentials doğru mu?
- Headless mode'u kapatıp tarayıcıyı görün:
  ```json
  "settings": {
    "headless": false
  }
  ```

## 📱 Telegram'dan Takip

Bot çalışırken Telegram'dan şu mesajları alacaksınız:

1. **Başlangıç**: `🤖 Vize Randevu Botu başlatıldı!`
2. **Tarama**: `🔍 Tarama devam ediyor... (Deneme #10)`
3. **Randevu bulundu**: `🎯 RANDEVU BULUNDU!`
4. **Rezervasyon**: `✅ REZERVASYON BAŞARILI!`
5. **SMS bekleniyor**: `💳 3D SECURE SMS KODUNU GİRİN:`
   - Bu mesajı aldığınızda bankanızdan gelen SMS kodunu Telegram'a yazın
   - Örnek: `123456`
6. **Tamamlandı**: `🎉 ÖDEME TAMAMLANDI!`

## ⚙️ Önerilen Ayarlar

### İlk Kullanım (Test)
```json
{
  "settings": {
    "polling_interval_minutes": 5,    // Daha sık kontrol
    "headless": false,                // Tarayıcıyı gör
    "screenshot_on_error": true,      // Hata ekran görüntüleri
    "max_retries": 3
  }
}
```

### Gerçek Kullanım (7/24)
```json
{
  "settings": {
    "polling_interval_minutes": 10,   // Standart interval
    "headless": true,                 // Arka planda çalış
    "screenshot_on_error": true,      // Hata ekran görüntüleri
    "max_retries": 5                  // Daha fazla deneme
  }
}
```

## 🔄 Botu Durdurma

```bash
# Ctrl+C ile durdur
# veya
pkill -f main.py
```

Bot, graceful shutdown yapacak ve tüm kaynakları temizleyecektir.

## 📊 Log Dosyaları

Loglar `logs/` klasöründe saklanır:
```bash
# Son logları görüntüle
tail -f logs/VisaBot_*.log

# Hata loglarını filtrele
grep ERROR logs/VisaBot_*.log
```

## 🎓 Sonraki Adımlar

1. ✅ İlk testi başarıyla tamamladınız mı?
2. 📖 [README.md](README.md) dosyasını okuyun (detaylı bilgi)
3. 🔧 Ayarları ihtiyacınıza göre optimize edin
4. 🚀 7/24 modda çalıştırın

## 💡 Pro İpuçları

- **Screen kullanın**: Sunucuda 7/24 çalıştırmak için
  ```bash
  screen -S visa-bot
  python main.py
  # Ctrl+A+D ile detach
  # screen -r visa-bot ile geri dön
  ```

- **Systemd service**: Otomatik başlatma için
  ```bash
  sudo nano /etc/systemd/system/visa-bot.service
  sudo systemctl enable visa-bot
  sudo systemctl start visa-bot
  ```

- **Cron job**: Belirli saatlerde çalıştırma
  ```bash
  crontab -e
  # Her gün 09:00'da başlat
  0 9 * * * cd /path/to/visa-bot && python main.py
  ```

## 🆘 Yardım

Sorun mu yaşıyorsunuz?
1. `logs/` klasöründeki log dosyalarını kontrol edin
2. `headless: false` yaparak tarayıcıyı görün
3. README.md'deki Troubleshooting bölümüne bakın
4. Screenshot'ları inceleyin

---

**🎉 Başarılar! Randevunuz yakında! 🇳🇱**
