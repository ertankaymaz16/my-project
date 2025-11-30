# 🚀 QUICK START - IP BAN FIX

## ⚡ 3-MINUTE SETUP

### Problem
Getting **Error 403201** from VFS Global? Your IP is banned.

### Solution
Use a proxy to change your IP address.

---

## 📝 STEPS

### 1️⃣ Get a Proxy (Choose One)

#### Option A: Smartproxy (Recommended - $75/month)
1. Go to https://smartproxy.com/
2. Sign up and get credentials
3. Note: `server`, `username`, `password`

#### Option B: Webshare (Budget - $3/month)
1. Go to https://www.webshare.io/
2. Sign up for free trial or paid plan
3. Get proxy list from dashboard

#### Option C: Free Proxy (Not Recommended)
1. Go to https://www.freeproxylists.net/
2. Find a working proxy
3. Test it first!

---

### 2️⃣ Update config.json

```bash
# Copy example config
cp config.json.example config.json

# Edit config.json
nano config.json  # or use any text editor
```

**Add your proxy details:**

```json
{
  "proxy": {
    "enabled": true,
    "server": "http://gate.smartproxy.com:7000",
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD"
  },
  "settings": {
    "clear_cache_on_start": true,
    "headless": false
  }
}
```

**Replace:**
- `YOUR_USERNAME` with your actual proxy username
- `YOUR_PASSWORD` with your actual proxy password
- `gate.smartproxy.com:7000` with your proxy server

---

### 3️⃣ Test Proxy

```bash
python test_proxy.py
```

**Expected Output:**
```
✅ Your original IP: 123.45.67.89
✅ Your proxy IP: 98.76.54.32
✅ IP Changed: YES
✅ VFS Global accessible - no 403 error!
🎉 ALL TESTS PASSED!
```

**If test fails:**
- Check proxy credentials
- Try different proxy
- See troubleshooting below

---

### 4️⃣ Run Bot

```bash
python main.py
```

**Success indicators:**
- ✅ No 403 error
- ✅ Browser opens
- ✅ VFS Global page loads
- ✅ Can login

---

## 🔧 CONFIGURATION EXAMPLES

### Smartproxy
```json
{
  "proxy": {
    "enabled": true,
    "server": "http://gate.smartproxy.com:7000",
    "username": "sp12345678",
    "password": "abc123xyz"
  }
}
```

### Bright Data
```json
{
  "proxy": {
    "enabled": true,
    "server": "http://brd.superproxy.io:22225",
    "username": "brd-customer-hl_12345678-zone-residential",
    "password": "abc123xyz"
  }
}
```

### Webshare
```json
{
  "proxy": {
    "enabled": true,
    "server": "http://proxy.webshare.io:80",
    "username": "user123",
    "password": "pass123"
  }
}
```

### NordVPN SOCKS5
```json
{
  "proxy": {
    "enabled": true,
    "server": "socks5://proxy-nl.nordvpn.com:1080",
    "username": "your_email@example.com",
    "password": "your_nordvpn_password"
  }
}
```

### Free Proxy (No Auth)
```json
{
  "proxy": {
    "enabled": true,
    "server": "http://123.45.67.89:8080"
  }
}
```

---

## 🐛 TROUBLESHOOTING

### ❌ Test shows "Proxy connection failed"

**Fix:**
```bash
# Test proxy manually
curl -x http://user:pass@proxy.com:8080 https://api.ipify.org

# If this fails, proxy is not working
# Try different proxy or check credentials
```

### ❌ Test shows "IP did not change"

**Fix:**
- Proxy is not being used
- Check `"enabled": true` in config
- Verify proxy server format (must start with `http://` or `socks5://`)

### ❌ Test shows "Still getting 403 error"

**Fix:**
- Proxy IP is also blacklisted
- Try different proxy server
- Use residential proxy instead of datacenter
- Try proxy from different country

### ❌ "Invalid proxy configuration"

**Fix:**
```json
// Wrong:
"server": "proxy.com:8080"

// Correct:
"server": "http://proxy.com:8080"
```

---

## 📊 PROXY COMPARISON

| Service | Price | Quality | Speed | Recommended |
|---------|-------|---------|-------|-------------|
| Bright Data | $$$$ | ⭐⭐⭐⭐⭐ | Fast | Best |
| Smartproxy | $$$ | ⭐⭐⭐⭐ | Fast | Good |
| IPRoyal | $$ | ⭐⭐⭐⭐ | Medium | Budget |
| Webshare | $ | ⭐⭐⭐ | Fast | Testing |
| Free | Free | ⭐ | Slow | Not Recommended |

---

## 💡 TIPS

### 1. Use Residential Proxies
- Harder to detect
- More reliable
- Worth the extra cost

### 2. Choose Proxy Location
- Turkish proxies: Best for VFS Turkey
- Dutch proxies: Also good (target country)
- Avoid: Same country as your real IP

### 3. Keep Cache Clearing Enabled
```json
"settings": {
  "clear_cache_on_start": true
}
```

### 4. Monitor Proxy Health
- Check proxy speed regularly
- Have backup proxy ready
- Rotate IPs if possible

---

## 📚 MORE HELP

- **Detailed Guide**: See `PROXY_SETUP_GUIDE.md`
- **Full Changes**: See `CHANGES_SUMMARY.md`
- **Problem Explanation**: See `IP_BAN_SOLUTION.md`

---

## ✅ CHECKLIST

Before running bot:
- [ ] Proxy service selected
- [ ] Credentials obtained
- [ ] config.json updated
- [ ] `proxy.enabled = true`
- [ ] Test script passed
- [ ] IP address changed
- [ ] No 403 error in test

---

## 🎉 SUCCESS!

If test passes, you're ready to run the bot:

```bash
python main.py
```

The 403 error should be gone! 🎊

---

**Need help?** Read the detailed guides or check the logs in `logs/` directory.
