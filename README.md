# 🔒 CyberAI Telegram Bot

A unified Telegram bot that integrates **Camera Capture** (own-cam) and **URL Masker** modules into a single conversational interface.

## ✨ Features

### 📷 Camera Capture
- Deploy a Flask web server that captures camera frames from visitors
- Support for **front**, **back**, and **both** camera modes
- Real-time image delivery directly to your Telegram chat
- Configurable redirect URL and timing
- IP and activity logging

### 🔗 URL Masker
- Mask any URL with a fake domain using the `@` technique
- Automatic URL shortening via TinyURL, Dagd, Clckru, Osdb
- Multiple masking methods (@ method, subdomain, path, query)
- Generates ready-to-copy masked URLs

### 📷+🔗 Combined Mode
- Start camera server → automatically mask the server URL
- One-click workflow for the complete pipeline

### 📂 File Management
- Browse and download captured images
- Export all captures as ZIP
- View and download activity logs
- Clear data with confirmation

### ⚙️ Settings
- Default camera mode
- Default redirect time
- Notification toggle
- Clear all data

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd telegram
pip install -r requirements.txt
```

### 2. Configure Environment

Edit the `.env` file:

```bash
BOT_TOKEN=7312555678:AAFyZsQAd1dsnCbW2u4NJbVQfbFpIATitG8
ADMIN_IDS=              # Leave empty — first user becomes admin
CAM_SERVER_PORT=5000
```

### 3. Run the Bot

```bash
python run.py
```

### 4. Open Telegram

Search for **@telecyber_ai_bot** and send `/start`.

---

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/start` | Open main menu |
| `/help` | Show detailed help |
| `/status` | Check server status |
| `/stop` | Stop running camera server |
| `/myid` | Show your Telegram user ID |
| `/cancel` | Cancel current operation |

---

## 📁 Folder Structure

```
telegram/
├── own-cam/              # Original camera capture module (preserved)
│   ├── eye.py            # Advanced camera server (front/back/both)
│   ├── main.py           # Basic camera server
│   ├── mobile.py         # Mobile-optimized server
│   ├── index.html        # Motivational landing page
│   ├── captured/         # Captured images stored here
│   └── ip_logs/          # Activity logs
├── url_masker/           # Original URL masker module (preserved)
│   ├── main.py           # URL masking tool
│   └── README.md         # URL masker documentation
├── bot/                  # Telegram bot package
│   ├── main.py           # Application builder & runner
│   ├── config.py         # Configuration management
│   ├── handlers/         # Telegram command & callback handlers
│   │   ├── start.py      # /start, /help, navigation
│   │   ├── cam_handler.py    # Camera capture flow
│   │   ├── masker_handler.py # URL masker flow
│   │   ├── logs_handler.py   # Captures & logs viewer
│   │   └── settings_handler.py # Bot settings
│   ├── services/         # Business logic wrappers
│   │   ├── cam_service.py    # Camera server lifecycle
│   │   ├── masker_service.py # URL masking operations
│   │   └── tunnel_service.py # Optional tunnel management
│   ├── middleware/
│   │   └── auth.py       # Authorization decorator
│   ├── utils/
│   │   ├── keyboards.py  # Inline keyboard builders
│   │   ├── messages.py   # Message templates
│   │   └── helpers.py    # File & formatting utilities
│   └── database/
│       └── session.py    # JSON session & history storage
├── requirements.txt      # Python dependencies
├── .env                  # Environment configuration
├── .env.example          # Environment template
├── run.py                # Entry point: python run.py
└── README.md             # This file
```

---

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot API token | Required |
| `ADMIN_IDS` | Comma-separated admin user IDs | Empty (auto-register first user) |
| `CAM_SERVER_PORT` | Port for the camera Flask server | `5000` |
| `CAM_SERVER_HOST` | Host to bind the camera server | `0.0.0.0` |
| `LOG_LEVEL` | Logging level | `INFO` |

---

## 📷 Camera Capture Workflow

1. **Start** → Tap "📷 Camera Capture" in menu
2. **Configure** → Select camera mode (front/back/both)
3. **Redirect** → Enter where the target redirects after capture
4. **Timing** → Enter how long to capture before redirecting
5. **Server URL** → Enter your public URL (from ngrok/Cloudflare)
6. **Confirm** → Review settings and deploy
7. **Monitor** → Captured images arrive in your chat in real-time
8. **Stop** → Tap "⏹ Stop Server" when done

### Making Your Server Public

The camera server runs locally. To make it accessible from the internet:

**Option A: ngrok**
```bash
ngrok http 5000
```

**Option B: Cloudflare Tunnel**
```bash
cloudflared tunnel --url http://localhost:5000
```

Use the generated public URL when the bot asks for "server's public URL".

---

## 🔗 URL Masker Workflow

1. **Start** → Tap "🔗 URL Masker" in menu
2. **URL** → Enter the original URL to mask
3. **Domain** → Enter the fake domain (e.g., google.com)
4. **Keywords** → Optionally add keywords (e.g., login)
5. **Result** → Get masked URLs in all 4 methods

### How Masking Works

```
https://google.com-login@tinyurl.com/abc123
        └─────┬──────┘└──┬──┘ └────────┬────────┘
         Fake Domain   Keyword     Real Short URL
```

---

## 🛡️ Security

- **Admin-only access** — Only authorized users can use the bot
- **Auto-registration** — First user to `/start` becomes admin
- **Input validation** — All user inputs are validated
- **File sanitization** — Filenames are sanitized before saving
- **Graceful errors** — All exceptions are caught and displayed cleanly

---

## 🛡️ Ethical Use Only

This tool is for **authorized purposes only**:
- ✅ Security awareness training
- ✅ Authorized penetration testing
- ✅ Educational demonstrations

**NOT for:**
- ❌ Unauthorized surveillance
- ❌ Phishing or fraud
- ❌ Any illegal activities

---

## 📦 Dependencies

- `python-telegram-bot` — Telegram Bot API
- `flask` — Camera capture web server
- `requests` — HTTP library
- `pyshorteners` — URL shortening services
- `python-dotenv` — Environment variable loading
- `watchdog` — File system monitoring

---

**Version:** 1.0
**Bot:** @telecyber_ai_bot
