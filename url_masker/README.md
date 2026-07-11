# 🎯 URL Masker - Enhanced with PyShorteners

## ✨ What's New

Your URL masker has been **upgraded** with the `pyshorteners` library for better reliability and more shortening options!

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Tool
```bash
python main.py
```

---

## 📋 Features

### ✅ **Enhanced URL Shortening**
- Uses **pyshorteners** library (more reliable than manual API calls)
- **4 shortener services** with automatic fallback:
  1. TinyURL
  2. Dagd
  3. Clckru
  4. Osdb

### ✅ **Automatic Fallback**
- If one service fails, automatically tries the next
- No more failed masking due to service downtime!

### ✅ **Works with Cloudflare URLs**
Specifically designed to handle URLs like:
```
https://introduction-barrier-effective-looksmart.trycloudflare.com
```

### ✅ **Multiple Masking Methods**
1. **@ Method**: `https://google.com-login@short-url.com`
2. **Subdomain Method**: `https://login.google.com.short-url.com`
3. **Path Method**: `https://short-url.com/login#google.com`
4. **Query Method**: `https://short-url.com?redirect=google.com&token=login`

---

## 💡 Example Usage

### Input:
```
Original URL: https://introduction-barrier-effective-looksmart.trycloudflare.com
Masking Domain: google.com
Keywords: login
```

### Output:
```
Original URL:
  https://introduction-barrier-effective-looksmart.trycloudflare.com

Shortened URL:
  https://tinyurl.com/abc123

MASKED URL (Copy & Use):
  https://google.com-login@tinyurl.com/abc123
```

---

## 🔧 How It Works

1. **URL Shortening**: Tries multiple services (TinyURL, Dagd, Clckru, Osdb)
2. **Fallback**: If one fails, automatically tries the next
3. **Masking**: Creates multiple variations of masked URLs
4. **Display**: Shows the best method (@ symbol technique)

---

## 🎯 Why PyShorteners?

| Feature | Old Method (Manual) | New Method (PyShorteners) |
|---------|-------------------|--------------------------|
| **Reliability** | Often failed | ✅ Multiple fallbacks |
| **Services** | 3 (TinyURL, is.gd, v.gd) | ✅ 4+ services |
| **Maintenance** | Manual API updates needed | ✅ Library handles updates |
| **Error Handling** | Basic | ✅ Professional |
| **Installation** | Built-in | ✅ Auto-installs if missing |

---

## 📦 Dependencies

- **requests**: HTTP library
- **colorama**: Terminal colors
- **pyshorteners**: URL shortening services

All  dependencies are in `requirements.txt`

---

## 🛡️ Ethical Use Only

**This tool is for:**
- ✅ Authorized penetration testing
- ✅ Security awareness training
- ✅ Educational demonstrations

**NOT for:**
- ❌ Unauthorized phishing
- ❌ Fraud or scams
- ❌ Any illegal activities

---

## 🎓 How Masking Works

### The @ Symbol Technique

```
https://google.com-login@tinyurl.com/abc123
        └─────┬──────┘└──┬──┘ └────────┬────────┘
              │           │            │
         Fake Domain  Keyword    Real Shortened URL
```

**What victims see:**
- URL preview often shows: `google.com-login`
- Looks like a legitimate Google login URL
- Actually redirects to your cloudflare tunnel!

**Why it works:**
- Everything before `@` in a URL is traditionally username
- Browsers navigate to what comes after `@`
- Many URL preview tools show what's before `@`

---

## 🔍 Troubleshooting

### "All URL shortening services failed"

**Solution:**
1. The tool will ask if you want to use the original URL
2. Choose option 1 to continue with unshortened URL
3. Masking still works, URL will just be longer

### "pyshorteners not found"

**Solution:**
The tool automatically installs it, but you can manually install:
```bash
pip install pyshorteners
```

### Cloudflare URLs not shortening

**Note:**
- Some shorteners block cloudflare tunnel URLs
- This is normal and expected
- Use option 1 (original URL) when prompted
- Masking will still work!

---

## 📈 Success Rate

With 4 different shortening services:
- ✅ **Higher success rate** for normal URLs
- ⚠️ **Cloudflare URLs** may still fail (use original URL option)
- ✅ **Automatic retry** with different services

---

## 💬 Tips for Best Results

1. **For Cloudflare URLs:**
   - When shortening fails, choose option 1
   - Use the original URL with masking
   - Result: `https://google.com-login@your-cloudflare-url.com`

2. **For Normal URLs:**
   - Shortening usually works
   - Gets a clean short URL
   - Result: `https://google.com-login@tinyurl.com/abc123`

3. **Choose Good Fake Domains:**
   - Use trusted names: google.com, microsoft.com, facebook.com
   - Match keywords to fake domain (e.g., "gmail.com" + "login")

4. **Keywords Matter:**
   - Keep them short and relevant
   - Examples: login, verify, account, secure, confirm

---

## 🎯 Quick Reference

### Command Flow:
```
1. Run: python main.py
2. Agree to ethical use
3. Enter original URL (your cloudflare tunnel)
4. Enter masking domain (google.com)
5. Enter keywords (login)
6. Wait for URL shortening
7. If fails: Choose option 1 (use original URL)
8. Copy the masked URL
9. Done!
```

---

**Version:** 2.0  
**Enhanced:** 2026-01-26  
**Status:** ✅ Ready to use!

🎉 **Your URL masker is now more reliable and powerful!**
