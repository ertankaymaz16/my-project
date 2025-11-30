# 🏗️ Mimari Dokümantasyonu

## Teknoloji Yığını Seçim Gerekçeleri

### Python 3.8+
**Neden seçildi:**
- Zengin kütüphane ekosistemi (email, asyncio, json)
- Mükemmel async/await desteği
- Kolay hata yönetimi ve exception handling
- Cross-platform uyumluluk
- Hızlı prototipleme ve geliştirme

**Alternatifler:**
- Node.js: Daha hızlı olabilir ama email/IMAP desteği zayıf
- Go: Performanslı ama kütüphane ekosistemi sınırlı
- Java: Ağır ve verbose

### Playwright (Puppeteer değil)
**Neden seçildi:**
- **Anti-Detection**: Chromium'un gerçek tarayıcı parmak izini kullanır
- **Stealth Mode**: `navigator.webdriver` otomatik olarak gizlenir
- **Cross-Browser**: Chromium, Firefox, WebKit desteği
- **Modern API**: Async/await native desteği
- **Stabilite**: Bellek yönetimi mükemmel, memory leak yok
- **Context Isolation**: Her session için ayrı context
- **Auto-wait**: Element'lerin hazır olmasını otomatik bekler

**Puppeteer'e göre avantajları:**
- Daha iyi anti-detection
- Daha stabil (özellikle uzun süreli çalışmalarda)
- Daha iyi hata mesajları
- Built-in stealth features

### Asyncio
**Neden seçildi:**
- Non-blocking I/O ile 7/24 çalışma
- Telegram ve Mail kontrolü paralel çalışabilir
- Bellek verimliliği (thread'lere göre)
- Python'un native async desteği

### IMAP (Email)
**Neden seçildi:**
- Gmail/Outlook ile doğrudan entegrasyon
- Gerçek zamanlı email okuma
- Güvenli bağlantı (SSL/TLS)
- OTP kodlarını otomatik çekme

**Alternatifler:**
- Gmail API: Daha karmaşık OAuth2 gerektirir
- POP3: Eski ve sınırlı
- Webhook: Email provider desteği gerektirir

### Telegram Bot API
**Neden seçildi:**
- Kolay entegrasyon
- Gerçek zamanlı bildirimler
- İki yönlü iletişim (human-in-the-loop için ideal)
- Ücretsiz ve güvenilir
- Resim/dosya gönderme desteği

**Alternatifler:**
- WhatsApp: API karmaşık ve ücretli
- SMS: Pahalı
- Email: Yavaş ve spam riski

---

## Modül Mimarisi

### 1. Browser Manager (`modules/browser.py`)
**Sorumluluklar:**
- Playwright browser lifecycle yönetimi
- Stealth configuration
- Cookie yönetimi (session persistence)
- Screenshot alma
- Context isolation

**Anti-Detection Özellikleri:**
- Custom user agent
- Random viewport sizes
- Geolocation spoofing (Bursa coordinates)
- Timezone setting (Europe/Istanbul)
- WebDriver flag hiding
- Chrome object mocking
- Permissions mocking

**Bellek Yönetimi:**
- Proper cleanup on shutdown
- Context reuse
- Automatic page closure

### 2. Auth Manager (`modules/auth.py`)
**Sorumluluklar:**
- VFS Global login
- OTP verification
- Session validation
- Cookie persistence

**Akış:**
```
1. Navigate to login page
2. Fill email + password (human-like typing)
3. Click login button
4. Detect OTP requirement
5. Wait for OTP email (via MailHandler)
6. Extract OTP code
7. Submit OTP
8. Verify login success
9. Save cookies
```

**Retry Mekanizması:**
- Max 3 deneme
- Her denemede 2-3 saniye bekleme
- Hata durumunda screenshot

### 3. Mail Handler (`modules/mail_handler.py`)
**Sorumluluklar:**
- IMAP bağlantısı
- Email okuma
- OTP extraction (regex)
- Async wrapper

**OTP Extraction Patterns:**
```python
r'\b(\d{6})\b'              # 6-digit code
r'\b(\d{4})\b'              # 4-digit code
r'code[:\s]+(\d{4,8})'      # "code: 123456"
r'OTP[:\s]+(\d{4,8})'       # "OTP: 123456"
```

**Timeout:**
- 60 saniye (configurable)
- 5 saniyede bir kontrol
- Son 5 email'i tara

### 4. Appointment Manager (`modules/appointment.py`)
**Sorumluluklar:**
- Randevu tarama (polling)
- Filtre uygulama (location, visa type, people)
- Slot detection
- Rezervasyon
- Form doldurma

**Polling Stratejisi:**
```
while True:
    1. Navigate to appointment page
    2. Apply filters (Bursa, Tourist, 2 people)
    3. Check availability
    4. If found:
        - Notify via Telegram
        - Book immediately
        - Break loop
    5. If not found:
        - Random delay (8-12 minutes)
        - Continue loop
```

**Anti-Bot Measures:**
- Random delays between actions
- Human-like typing speed
- Mouse movements
- Random scroll
- Realistic viewport

### 5. Payment Manager (`modules/payment.py`)
**Sorumluluklar:**
- Payment form doldurma
- 3D Secure handling
- Human-in-the-loop (SMS code)
- Payment verification

**3D Secure Flow:**
```
1. Fill payment form
2. Click pay button
3. Detect 3D Secure iframe
4. Request SMS code via Telegram
5. Wait for user response (max 5 minutes)
6. Enter SMS code
7. Submit
8. Verify payment success
```

**Iframe Handling:**
- Automatic iframe detection
- Context switching
- Fallback to main page

### 6. Telegram Bot (`modules/telegram_bot.py`)
**Sorumluluklar:**
- Bildirimler gönderme
- SMS kodu alma (human-in-the-loop)
- Screenshot gönderme
- Durum güncellemeleri

**Message Types:**
- Startup notification
- Polling status (her 10 denemede bir)
- Appointment found
- Reservation success
- SMS code request
- Payment success
- Error notifications

**Human-in-the-Loop:**
```python
async def request_sms_code():
    1. Set waiting_for_sms = True
    2. Send Telegram message
    3. Wait for user response (asyncio.Event)
    4. Extract code from message (regex)
    5. Return code
    6. Timeout after 5 minutes
```

### 7. Logger (`utils/logger.py`)
**Sorumluluklar:**
- Renkli konsol logging
- File logging (rotation)
- Phase tracking
- Error tracking

**Log Levels:**
- DEBUG: Detaylı debug bilgileri (sadece file)
- INFO: Genel bilgilendirme (console + file)
- WARNING: Uyarılar
- ERROR: Hatalar
- CRITICAL: Kritik hatalar

**File Rotation:**
- Max 10MB per file
- 5 backup files
- Daily rotation

### 8. Stealth Helper (`utils/stealth.py`)
**Sorumluluklar:**
- Anti-detection scripts
- Human-like behavior simulation
- Random delays
- Mouse movements

**Features:**
- `add_stealth_scripts()`: WebDriver hiding, chrome object mocking
- `random_delay()`: Human-like delays
- `human_like_typing()`: Realistic typing speed
- `random_mouse_movement()`: Mouse simulation
- `scroll_randomly()`: Scroll simulation
- `wait_for_element_safely()`: Safe element waiting
- `click_with_retry()`: Retry mechanism

---

## Veri Akışı

```
┌─────────────────────────────────────────────────────────────┐
│                         MAIN.PY                             │
│                    (Orchestrator)                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├─────────────────────────────────┐
                            │                                 │
                            ▼                                 ▼
                    ┌───────────────┐               ┌──────────────┐
                    │ BrowserManager│               │  Telegram    │
                    └───────────────┘               │  Notifier    │
                            │                       └──────────────┘
                            │                               │
                            ▼                               │
                    ┌───────────────┐                       │
                    │  AuthManager  │◄──────────────────────┤
                    └───────────────┘                       │
                            │                               │
                            ├───────────────┐               │
                            │               │               │
                            ▼               ▼               │
                    ┌──────────┐    ┌─────────────┐        │
                    │   Mail   │    │ Appointment │        │
                    │ Handler  │    │   Manager   │◄───────┤
                    └──────────┘    └─────────────┘        │
                                            │               │
                                            ▼               │
                                    ┌──────────────┐        │
                                    │   Payment    │        │
                                    │   Manager    │◄───────┘
                                    └──────────────┘
```

---

## Hata Yönetimi Stratejisi

### 1. Retry Mekanizması
```python
for attempt in range(max_retries):
    try:
        # Operation
        return success
    except Exception as e:
        logger.error(f"Attempt {attempt + 1} failed: {e}")
        if attempt == max_retries - 1:
            raise
        await asyncio.sleep(delay)
```

### 2. Screenshot on Error
```python
try:
    # Critical operation
except Exception as e:
    screenshot_path = await browser.save_screenshot("error")
    await telegram.notify_error(str(e), screenshot_path)
```

### 3. Graceful Shutdown
```python
def signal_handler(signum, frame):
    logger.warning("Shutting down...")
    asyncio.create_task(shutdown())
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

### 4. Session Recovery
```python
async def check_session():
    if not await auth.check_session_valid():
        logger.warning("Session expired, re-logging...")
        await auth.login()
```

---

## Performans Optimizasyonları

### 1. Async/Await
- Non-blocking I/O
- Paralel işlemler (Telegram + Email)
- Efficient resource usage

### 2. Context Reuse
- Tek browser instance
- Cookie persistence
- Session reuse

### 3. Smart Polling
- Configurable interval
- Random delays (anti-bot)
- Exponential backoff on errors

### 4. Memory Management
- Proper cleanup
- No memory leaks
- Log rotation

---

## Güvenlik Önlemleri

### 1. Credential Management
- Config file (not in code)
- .gitignore ile koruma
- No hardcoded secrets

### 2. Secure Connections
- HTTPS only
- SSL/TLS for email
- Secure Telegram API

### 3. Data Privacy
- No logging of sensitive data
- Screenshot'larda kart bilgileri blur (TODO)
- Local storage only

### 4. Anti-Detection
- Stealth mode
- Human-like behavior
- Random delays
- Realistic user agent

---

## Ölçeklenebilirlik

### Mevcut Durum
- Single instance
- Single user
- Single appointment

### Gelecek İyileştirmeler
1. **Multi-User Support**
   - Database integration
   - User queue system
   - Separate sessions per user

2. **Distributed System**
   - Multiple bot instances
   - Load balancing
   - Redis for coordination

3. **Cloud Deployment**
   - Docker containerization
   - Kubernetes orchestration
   - Auto-scaling

4. **Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Alert system

---

## Test Stratejisi

### Unit Tests (TODO)
```python
# test_auth.py
async def test_login_success():
    auth = AuthManager(...)
    result = await auth.login()
    assert result == True

# test_mail.py
def test_otp_extraction():
    mail = MailHandler(...)
    otp = mail._extract_otp_from_email(...)
    assert otp == "123456"
```

### Integration Tests (TODO)
```python
# test_flow.py
async def test_full_flow():
    bot = VisaBot()
    await bot.initialize()
    # Mock appointment availability
    result = await bot.run()
    assert result == True
```

### E2E Tests
- Manuel testing with real VFS site
- Headless: false mode
- Screenshot verification

---

## Deployment Seçenekleri

### 1. Local Machine
```bash
python main.py
```
**Pros:** Kolay, ücretsiz
**Cons:** Bilgisayar açık kalmalı

### 2. VPS (DigitalOcean, Linode)
```bash
screen -S visa-bot
python main.py
```
**Pros:** 7/24 çalışır, ucuz ($5/month)
**Cons:** Manuel setup

### 3. Docker
```dockerfile
FROM python:3.9-slim
RUN playwright install chromium
COPY . /app
CMD ["python", "main.py"]
```
**Pros:** Portable, reproducible
**Cons:** Biraz daha karmaşık

### 4. Cloud Functions (AWS Lambda, Google Cloud Functions)
**Pros:** Serverless, ölçeklenebilir
**Cons:** Playwright desteği zor, cold start

---

## Bakım ve Güncelleme

### Selector Güncellemeleri
VFS sitesi değiştiğinde:
1. Chrome DevTools ile yeni selector'ları bul
2. İlgili modülü güncelle (auth.py, appointment.py, payment.py)
3. Test et

### Dependency Updates
```bash
pip list --outdated
pip install --upgrade <package>
pip freeze > requirements.txt
```

### Log Monitoring
```bash
tail -f logs/VisaBot_*.log | grep ERROR
```

---

## Bilinen Sınırlamalar

1. **CAPTCHA**: Manuel çözüm gerektirir
2. **Rate Limiting**: VFS tarafından ban riski
3. **Site Değişiklikleri**: Selector'lar güncellenmelidir
4. **3D Secure**: Human-in-the-loop gerektirir
5. **Email Delay**: OTP email'i geç gelebilir

---

## Katkıda Bulunma

1. Fork the repo
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

**Kod Standartları:**
- PEP 8 compliance
- Type hints
- Docstrings
- Error handling
- Logging

---

**Mimari Tasarım: Modüler, Ölçeklenebilir, Bakımı Kolay** 🏗️
