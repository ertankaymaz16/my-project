# Browser.py Refactor Documentation

## 🎯 Refactor Objectives

This refactor addresses critical issues with the Hollanda Vize Randevu Bot running on MacOS (Apple Silicon) with Python 3.11 in a virtual environment.

---

## 🔧 Problems Solved

### 1. WAF/Cloudflare Blocking (Error 403201)
**Problem:** Bot was detected by VFS Global's WAF/Cloudflare protection due to browser fingerprinting.

**Solutions Implemented:**
- ✅ Added `--disable-blink-features=AutomationControlled` flag
- ✅ Removed automation flags with `ignore_default_args=['--enable-automation']`
- ✅ Fixed MacOS User-Agent (no randomization to avoid fingerprint inconsistency)
- ✅ Enhanced JavaScript stealth scripts to hide automation markers
- ✅ Added realistic browser properties (plugins, chrome object, permissions)
- ✅ Set consistent viewport (1920x1080) to avoid fingerprint changes
- ✅ Added realistic HTTP headers with proper Sec-Fetch-* headers

### 2. Chromium Crashes on MacOS (SEGV_ACCERR)
**Problem:** Chromium crashed with memory errors when running in headless mode on MacOS.

**Solutions Implemented:**
- ✅ Changed default `headless=False` (visible mode prevents crashes)
- ✅ Added `--disable-gpu` flag for MacOS stability
- ✅ Added `--disable-dev-shm-usage` for memory management
- ✅ Added `slow_mo=50` for more stable operation
- ✅ Increased timeouts to 60 seconds for resilience

### 3. Cookie Injection for Login Bypass
**Problem:** Need to bypass login screens using saved session cookies.

**Solutions Implemented:**
- ✅ Automatic cookie injection on browser start
- ✅ Checks for `cookies.json` file in project root
- ✅ Loads cookies into browser context before page creation
- ✅ Save/load cookie methods with error handling
- ✅ JSON format with UTF-8 encoding support

### 4. Consistency & Reliability
**Problem:** Random user agents and viewports caused detection issues.

**Solutions Implemented:**
- ✅ Fixed MacOS User-Agent: `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36`
- ✅ Fixed viewport: `1920x1080`
- ✅ Consistent geolocation (Bursa coordinates)
- ✅ Consistent locale and timezone (tr-TR, Europe/Istanbul)

---

## 📋 Key Changes

### Class Structure
```python
class BrowserManager:
    # Constants for consistency
    MACOS_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
    VIEWPORT = {'width': 1920, 'height': 1080}
    DEFAULT_TIMEOUT = 60000  # 60 seconds
    NAVIGATION_TIMEOUT = 60000
```

### Enhanced Launch Arguments
```python
launch_args = [
    '--disable-blink-features=AutomationControlled',  # CRITICAL
    '--disable-infobars',  # Remove automation banner
    '--disable-gpu',  # MacOS stability
    '--disable-dev-shm-usage',  # Memory management
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-web-security',
    '--ignore-certificate-errors',
    '--exclude-switches=enable-automation',  # Hide automation
]

# Remove automation flags
ignore_default_args=['--enable-automation']
```

### Cookie Injection Flow
```python
async def _create_context(self):
    # Create context with fixed settings
    self.context = await self.browser.new_context(**context_options)
    
    # AUTO-INJECT cookies if file exists
    if self.cookies_file.exists():
        await self._inject_cookies()
```

### Enhanced Stealth Scripts
```javascript
// Hide webdriver property
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// Add realistic plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => [/* Chrome PDF Plugin, PDF Viewer, Native Client */]
});

// Add chrome object
window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {}
};

// Mock hardware specs
Object.defineProperty(navigator, 'hardwareConcurrency', {
    get: () => 8
});

Object.defineProperty(navigator, 'deviceMemory', {
    get: () => 8
});
```

---

## 🚀 New Features

### 1. Automatic Cookie Injection
```python
browser = BrowserManager(cookies_file="cookies.json")
page = await browser.start()  # Automatically loads cookies if file exists
```

### 2. Session Validation
```python
is_valid = await browser.check_session()
if not is_valid:
    # Re-login required
```

### 3. Enhanced Screenshot
```python
screenshot_path = await browser.save_screenshot("error_state", full_page=True)
```

### 4. Page Information
```python
info = await browser.get_page_info()
# Returns: url, title, viewport, cookies_count, user_agent
```

### 5. Browser Restart
```python
new_page = await browser.restart()  # Clean restart with 2s delay
```

---

## 📝 Usage Examples

### Basic Usage
```python
from modules.browser import BrowserManager

async def main():
    # Initialize (headless=False for MacOS stability)
    browser = BrowserManager(headless=False)
    
    # Start browser with anti-detection
    page = await browser.start()
    
    # Navigate
    await page.goto("https://visa.vfsglobal.com/tur/tr/nld/")
    
    # Save cookies for next session
    await browser.save_cookies()
    
    # Close
    await browser.close()
```

### With Cookie Injection
```python
async def main():
    # Will automatically load cookies.json if exists
    browser = BrowserManager(
        headless=False,
        cookies_file="cookies.json"
    )
    
    page = await browser.start()
    
    # Navigate - should skip login if cookies valid
    await page.goto("https://visa.vfsglobal.com/tur/tr/nld/dashboard")
    
    # Check if session is valid
    if not await browser.check_session():
        print("Session expired, need to re-login")
    
    await browser.close()
```

### Error Recovery
```python
async def main():
    browser = BrowserManager(headless=False)
    
    try:
        page = await browser.start()
        await page.goto("https://example.com")
        
    except Exception as e:
        # Save screenshot for debugging
        await browser.save_screenshot("error")
        
        # Restart browser
        page = await browser.restart()
    
    finally:
        await browser.close()
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
python test_browser_refactor.py
```

### Test Coverage
1. ✅ Browser initialization with anti-detection
2. ✅ Cookie injection and persistence
3. ✅ Stealth features (webdriver hiding, plugins, etc.)
4. ✅ Session management and recovery
5. ✅ Screenshot functionality

---

## ⚙️ Configuration

### Recommended Settings for MacOS

```python
browser = BrowserManager(
    headless=False,  # IMPORTANT: False for MacOS stability
    user_data_dir="./browser_data",  # Persistent browser data
    cookies_file="cookies.json"  # Session persistence
)
```

### For Production (24/7 Operation)

```python
# In config.json
{
    "settings": {
        "headless": false,  # Keep false for MacOS
        "screenshot_on_error": true,
        "max_retries": 3
    }
}
```

---

## 🔍 Debugging

### Check Browser Fingerprint
```python
info = await browser.get_page_info()
print(f"User Agent: {info['user_agent']}")
print(f"Viewport: {info['viewport']}")
print(f"Cookies: {info['cookies_count']}")
```

### Verify Stealth Features
```python
# Check if webdriver is hidden
webdriver = await page.evaluate("navigator.webdriver")
print(f"Webdriver: {webdriver}")  # Should be None

# Check plugins
plugins = await page.evaluate("navigator.plugins.length")
print(f"Plugins: {plugins}")  # Should be > 0

# Check chrome object
chrome = await page.evaluate("typeof window.chrome")
print(f"Chrome: {chrome}")  # Should be 'object'
```

### Test on Bot Detection Sites
```python
await page.goto("https://bot.sannysoft.com/")
await browser.save_screenshot("bot_detection_test")
# Review screenshot to see detection results
```

---

## 🛡️ Anti-Detection Features

### Browser Fingerprint Consistency
- ✅ Fixed User-Agent (MacOS Chrome 121)
- ✅ Fixed Viewport (1920x1080)
- ✅ Consistent locale (tr-TR)
- ✅ Consistent timezone (Europe/Istanbul)
- ✅ Consistent geolocation (Bursa)

### JavaScript Stealth
- ✅ `navigator.webdriver` → `undefined`
- ✅ `navigator.plugins` → Realistic Chrome plugins
- ✅ `window.chrome` → Chrome object present
- ✅ `navigator.languages` → ['tr-TR', 'tr', 'en-US', 'en']
- ✅ `navigator.hardwareConcurrency` → 8
- ✅ `navigator.deviceMemory` → 8
- ✅ `navigator.connection` → 4g connection info

### HTTP Headers
- ✅ Realistic Accept headers
- ✅ Proper Accept-Language
- ✅ Sec-Fetch-* headers
- ✅ Connection: keep-alive

---

## 📊 Performance

### Timeouts
- Default timeout: 60 seconds
- Navigation timeout: 60 seconds
- Screenshot timeout: 30 seconds

### Delays
- Slow motion: 50ms between operations
- Restart delay: 2 seconds

---

## 🐛 Known Issues & Solutions

### Issue: "Chromium crashed" on MacOS
**Solution:** Use `headless=False` (already default in refactored code)

### Issue: "403 Forbidden" from VFS Global
**Solution:** 
1. Ensure cookies are loaded
2. Check User-Agent is consistent
3. Verify stealth scripts are applied
4. Use `headless=False`

### Issue: "Session expired"
**Solution:**
```python
if not await browser.check_session():
    # Save current cookies
    await browser.save_cookies()
    # Re-login logic here
```

---

## 🔄 Migration Guide

### Old Code
```python
browser = BrowserManager(headless=True)  # ❌ Crashes on MacOS
page = await browser.start()
```

### New Code
```python
browser = BrowserManager(
    headless=False,  # ✅ Stable on MacOS
    cookies_file="cookies.json"  # ✅ Auto-inject cookies
)
page = await browser.start()
```

---

## 📚 Dependencies

Ensure these are in `requirements.txt`:

```txt
playwright==1.40.0
aiofiles==23.2.1
```

Install Playwright browsers:
```bash
playwright install chromium
```

---

## 🎓 Best Practices

1. **Always use `headless=False` on MacOS** - Prevents crashes
2. **Save cookies after successful login** - Bypass login screens
3. **Use consistent fingerprint** - Don't randomize User-Agent
4. **Handle errors gracefully** - Use try/except with screenshots
5. **Check session validity** - Before critical operations
6. **Use proper timeouts** - 60 seconds for resilience

---

## 📞 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review screenshots for visual debugging
3. Test stealth features on bot detection sites
4. Verify Python 3.11 and venv are being used

---

## ✅ Checklist

Before deploying:
- [ ] Python 3.11 in venv
- [ ] `playwright install chromium` executed
- [ ] `headless=False` in production config
- [ ] `cookies.json` file prepared (if bypassing login)
- [ ] Test suite passes (`python test_browser_refactor.py`)
- [ ] Logs directory exists
- [ ] Config file properly set up

---

## 🎉 Summary

This refactor transforms `modules/browser.py` into a production-ready, anti-detection browser manager specifically optimized for:

✅ MacOS Apple Silicon stability  
✅ WAF/Cloudflare bypass  
✅ Cookie-based session persistence  
✅ Consistent browser fingerprinting  
✅ 24/7 reliable operation  

**Result:** A robust, stealth browser that can successfully automate VFS Global visa appointments without detection or crashes.
