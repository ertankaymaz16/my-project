# 🌐 PROXY SETUP GUIDE - IP BAN BYPASS

## PROBLEM SUMMARY
VFS Global's WAF (Web Application Firewall) has blocked your IP address, resulting in **Error 403201: "Olağandışı etkinlik nedeniyle erişim kısıtlandı"**. This is a network-level ban that cannot be bypassed with browser fingerprinting alone.

## SOLUTION: PROXY/VPN INTEGRATION

The bot now supports **proxy/VPN integration** to bypass IP bans by routing traffic through different IP addresses.

---

## 🚀 QUICK START

### 1. Update Your `config.json`

Copy `config.json.example` to `config.json` and configure the proxy section:

```json
{
  "proxy": {
    "enabled": true,
    "server": "http://your-proxy-server.com:8080",
    "username": "your_username",
    "password": "your_password"
  },
  "settings": {
    "clear_cache_on_start": true,
    "headless": false
  }
}
```

### 2. Proxy Configuration Options

#### Option A: HTTP/HTTPS Proxy
```json
"proxy": {
  "enabled": true,
  "server": "http://proxy.example.com:8080",
  "username": "user",
  "password": "pass"
}
```

#### Option B: SOCKS5 Proxy
```json
"proxy": {
  "enabled": true,
  "server": "socks5://proxy.example.com:1080",
  "username": "user",
  "password": "pass"
}
```

#### Option C: No Authentication
```json
"proxy": {
  "enabled": true,
  "server": "http://proxy.example.com:8080"
}
```

---

## 🔧 RECOMMENDED PROXY SERVICES

### Free Options (Limited)
1. **Free Proxy Lists**
   - https://www.freeproxylists.net/
   - https://hidemy.name/en/proxy-list/
   - ⚠️ Warning: Free proxies are often slow, unreliable, and may be blacklisted

### Paid Options (Recommended)

#### 1. **Bright Data (formerly Luminati)** ⭐ BEST
   - Website: https://brightdata.com/
   - Type: Residential proxies (most reliable)
   - Price: ~$500/month for 40GB
   - Format: `http://username:password@proxy.brightdata.com:22225`
   - **Why Best**: Real residential IPs, very hard to detect

#### 2. **Smartproxy**
   - Website: https://smartproxy.com/
   - Type: Residential proxies
   - Price: ~$75/month for 5GB
   - Format: `http://username:password@gate.smartproxy.com:7000`

#### 3. **Oxylabs**
   - Website: https://oxylabs.io/
   - Type: Residential/Datacenter proxies
   - Price: ~$300/month
   - Format: `http://username:password@pr.oxylabs.io:7777`

#### 4. **IPRoyal**
   - Website: https://iproyal.com/
   - Type: Residential proxies
   - Price: ~$7/GB (cheaper option)
   - Format: `http://username:password@geo.iproyal.com:12321`

#### 5. **Webshare**
   - Website: https://www.webshare.io/
   - Type: Datacenter proxies
   - Price: ~$2.99/month for 10 proxies
   - Format: `http://username:password@proxy.webshare.io:80`
   - **Budget Option**: Good for testing

### VPN Options

#### 1. **NordVPN** (with SOCKS5)
   - Website: https://nordvpn.com/
   - Price: ~$3-12/month
   - Setup: Use NordVPN's SOCKS5 proxy feature
   - Format: `socks5://username:password@proxy-nl.nordvpn.com:1080`

#### 2. **ExpressVPN**
   - Website: https://www.expressvpn.com/
   - Price: ~$8-12/month
   - Note: Requires manual setup with proxy

---

## 📋 SETUP INSTRUCTIONS

### Method 1: Using Paid Proxy Service (Recommended)

1. **Sign up for a proxy service** (e.g., Smartproxy, Bright Data)

2. **Get your proxy credentials**:
   - Server URL (e.g., `gate.smartproxy.com:7000`)
   - Username
   - Password

3. **Update config.json**:
```json
"proxy": {
  "enabled": true,
  "server": "http://gate.smartproxy.com:7000",
  "username": "your_smartproxy_username",
  "password": "your_smartproxy_password"
}
```

4. **Run the bot**:
```bash
python main.py
```

### Method 2: Using Local VPN + Proxy

1. **Install and connect to VPN** (NordVPN, ExpressVPN, etc.)

2. **Get SOCKS5 proxy details** from your VPN provider

3. **Update config.json**:
```json
"proxy": {
  "enabled": true,
  "server": "socks5://proxy-nl.nordvpn.com:1080",
  "username": "your_nordvpn_username",
  "password": "your_nordvpn_password"
}
```

### Method 3: Using SSH Tunnel (Advanced)

1. **Create SSH tunnel** to a remote server:
```bash
ssh -D 8080 -C -N user@your-server.com
```

2. **Update config.json**:
```json
"proxy": {
  "enabled": true,
  "server": "socks5://localhost:8080"
}
```

---

## 🧪 TESTING YOUR PROXY

### Test 1: Check IP Address
```python
import asyncio
from modules.browser import BrowserManager

async def test_proxy():
    proxy_config = {
        'server': 'http://your-proxy.com:8080',
        'username': 'user',
        'password': 'pass'
    }
    
    browser = BrowserManager(proxy_config=proxy_config)
    page = await browser.start()
    
    # Check IP
    await page.goto('https://api.ipify.org?format=json')
    content = await page.content()
    print(f"Your IP: {content}")
    
    await browser.close()

asyncio.run(test_proxy())
```

### Test 2: Check VFS Global Access
```python
async def test_vfs_access():
    proxy_config = {
        'server': 'http://your-proxy.com:8080',
        'username': 'user',
        'password': 'pass'
    }
    
    browser = BrowserManager(proxy_config=proxy_config)
    page = await browser.start()
    
    # Try accessing VFS Global
    await page.goto('https://visa.vfsglobal.com/tur/tr/nld/')
    
    # Check for 403 error
    title = await page.title()
    print(f"Page title: {title}")
    
    # Take screenshot
    await browser.save_screenshot('vfs_test')
    
    await browser.close()

asyncio.run(test_vfs_access())
```

---

## 🔍 TROUBLESHOOTING

### Issue 1: "Proxy connection failed"
**Solution**: 
- Verify proxy server URL format (http:// or socks5://)
- Check username/password are correct
- Test proxy with curl: `curl -x http://user:pass@proxy.com:8080 https://api.ipify.org`

### Issue 2: Still getting 403 error
**Solution**:
- Try a different proxy server/IP
- Use residential proxies instead of datacenter proxies
- Rotate proxy IPs frequently
- Clear cache: Set `"clear_cache_on_start": true` in config

### Issue 3: Slow performance
**Solution**:
- Use proxies closer to Turkey (TR region)
- Upgrade to faster proxy service
- Reduce `polling_interval_minutes` in config

### Issue 4: Proxy authentication failed
**Solution**:
- Check if username/password contain special characters
- URL-encode special characters: `@` → `%40`, `:` → `%3A`
- Example: `http://user%40domain:pass%3Aword@proxy.com:8080`

---

## 🎯 BEST PRACTICES

### 1. Use Residential Proxies
- **Why**: Residential IPs are from real ISPs, harder to detect
- **Services**: Bright Data, Smartproxy, Oxylabs

### 2. Rotate IPs Regularly
- Change proxy every few hours
- Use proxy services with automatic rotation

### 3. Match Proxy Location to Target
- Use Turkish proxies for VFS Turkey
- Or use proxies from Netherlands (target country)

### 4. Clear Cache on Each Run
```json
"settings": {
  "clear_cache_on_start": true
}
```

### 5. Monitor Proxy Health
- Check proxy speed and uptime
- Have backup proxies ready

### 6. Combine with Other Stealth Measures
- Keep `headless: false` for better stealth
- Use realistic delays between actions
- Don't run bot 24/7 (use scheduled intervals)

---

## 📊 PROXY COMPARISON

| Service | Type | Price | Speed | Detection Risk | Recommended |
|---------|------|-------|-------|----------------|-------------|
| Bright Data | Residential | $$$$ | Fast | Very Low | ⭐⭐⭐⭐⭐ |
| Smartproxy | Residential | $$$ | Fast | Low | ⭐⭐⭐⭐ |
| IPRoyal | Residential | $$ | Medium | Low | ⭐⭐⭐⭐ |
| Webshare | Datacenter | $ | Fast | Medium | ⭐⭐⭐ |
| Free Proxies | Mixed | Free | Slow | High | ⭐ |

---

## 🚨 IMPORTANT NOTES

### Cache Clearing
The bot now **automatically clears all browser cache** on startup when `clear_cache_on_start: true`. This includes:
- Browser data directory
- Playwright cache
- Session storage
- Local storage

This ensures a completely fresh start and removes any residual tracking data.

### Proxy Authentication
- Some proxies require IP whitelisting instead of username/password
- Check your proxy provider's documentation
- Add your server's IP to the whitelist if needed

### Legal Considerations
- Using proxies to bypass restrictions may violate terms of service
- Use responsibly and at your own risk
- Consider contacting VFS Global support to resolve IP ban legitimately

---

## 📞 SUPPORT

If you continue to experience issues:

1. **Check logs**: Look in `logs/` directory for detailed error messages
2. **Test proxy independently**: Use curl or browser to verify proxy works
3. **Try different proxy**: Some IPs may already be blacklisted
4. **Contact proxy provider**: They may have specific recommendations for your use case

---

## 🎉 SUCCESS INDICATORS

You'll know the proxy is working when:
- ✅ Bot starts without errors
- ✅ No 403201 error screen
- ✅ Can access VFS Global website
- ✅ Login page loads correctly
- ✅ Can navigate through appointment pages

---

## 📝 EXAMPLE CONFIGURATIONS

### Example 1: Smartproxy (Recommended)
```json
{
  "proxy": {
    "enabled": true,
    "server": "http://gate.smartproxy.com:7000",
    "username": "sp12345678",
    "password": "your_password_here"
  },
  "settings": {
    "clear_cache_on_start": true,
    "headless": false
  }
}
```

### Example 2: Bright Data
```json
{
  "proxy": {
    "enabled": true,
    "server": "http://brd.superproxy.io:22225",
    "username": "brd-customer-hl_12345678-zone-residential",
    "password": "your_password_here"
  },
  "settings": {
    "clear_cache_on_start": true,
    "headless": false
  }
}
```

### Example 3: Local SOCKS5 (VPN)
```json
{
  "proxy": {
    "enabled": true,
    "server": "socks5://localhost:1080"
  },
  "settings": {
    "clear_cache_on_start": true,
    "headless": false
  }
}
```

---

## 🔄 NEXT STEPS

1. ✅ Choose a proxy service from recommendations above
2. ✅ Sign up and get credentials
3. ✅ Update `config.json` with proxy details
4. ✅ Set `"clear_cache_on_start": true`
5. ✅ Run the bot: `python main.py`
6. ✅ Monitor logs for successful connection
7. ✅ Verify no 403 errors

**Good luck! The IP ban should now be bypassed.** 🎉
