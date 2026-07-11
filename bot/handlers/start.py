"""
CyberAI Bot — Start & Help Command Handlers
Handles /start, /help, /myid, /cancel commands and the main menu navigation.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from bot.middleware.auth import authorized_only
from bot.utils.keyboards import main_menu_keyboard, home_only_keyboard
from bot.utils.messages import (
    welcome_message, help_message, myid_message, operation_cancelled
)
from bot.database.session import (
    get_session, clear_conversation_state, log_activity, set_conversation_state
)
from bot.services.tunnel_service import CloudflareTunnelService

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
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command — show main menu and init tunnel service."""
    user = update.effective_user
    user_id = user.id
    log_activity(user_id, "start", "Main menu opened")

    # Clear any ongoing conversation state
    clear_conversation_state(user_id)
    context.user_data.clear()

    # Initialize tunnel service if not already initialized
    session = get_session(user_id)
    if 'tunnel_service' not in session or session['tunnel_service'] is None:
        session['tunnel_service'] = CloudflareTunnelService()
        set_conversation_state(user_id, "", session.get("data", {}))

    tunnel_service = session.get('tunnel_service')
    status = tunnel_service.get_status() if tunnel_service else {"running": False}

    # Check if tunnel is running
    tunnel_running = status.get("running", False)

    # Welcome message
    msg = welcome_message(user.first_name)

    # Build keyboard with tunnel status info if running
    keyboard = main_menu_keyboard()

    if tunnel_running:
        # Add tunnel controls as additional inline buttons
        tunnel_controls = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Restart Tunnel", callback_data="restart_tunnel"),
             InlineKeyboardButton("❌ Stop Tunnel", callback_data="stop_tunnel")],
            [InlineKeyboardButton("🌐 Show URL", callback_data="show_url")]
        ])
        # Send welcome message first, then tunnel controls
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboard)

        tunnel_info = (
            f"<b>🌐 Tunnel Status:</b> Running\n"
            f"<b>URL:</b> <code>{status.get('url', 'N/A')}</code>\n"
            f"<b>Masked URL:</b> <code>{status.get('masked_url', 'N/A')}</code>\n"
            f"<b>Port:</b> {tunnel_service.local_port if tunnel_service else 'N/A'}\n"
            f"<b>Started:</b> {status.get('start_time', 'N/A')}\n"
        )
        await update.message.reply_text(tunnel_info, parse_mode="HTML", reply_markup=tunnel_controls)
    else:
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboard)


@authorized_only
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command — show detailed help."""
    await update.message.reply_text(
        help_message(),
        parse_mode="HTML",
        reply_markup=home_only_keyboard(),
    )


@authorized_only
async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /myid command — show user's Telegram ID."""
    user = update.effective_user
    await update.message.reply_text(
        myid_message(user.id, user.username),
        parse_mode="HTML",
    )


@authorized_only
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command — cancel current operation."""
    user = update.effective_user

    # Clean up inactive tunnel on cancel
    from bot.services.cam_service import cam_service
    if not cam_service.is_running:
        session = get_session(user.id)
        tunnel_service = session.get('tunnel_service')
        if tunnel_service and tunnel_service.is_running():
            try:
                tunnel_service.stop_tunnel()
            except Exception:
                pass

    clear_conversation_state(user.id)
    context.user_data.clear()

    await update.message.reply_text(
        operation_cancelled(),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


@authorized_only
async def go_home_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'go_home' callback — return to main menu."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    # Clean up inactive tunnel on return home
    from bot.services.cam_service import cam_service
    if not cam_service.is_running:
        session = get_session(user.id)
        tunnel_service = session.get('tunnel_service')
        if tunnel_service and tunnel_service.is_running():
            try:
                tunnel_service.stop_tunnel()
            except Exception:
                pass

    clear_conversation_state(user.id)
    context.user_data.clear()

    await _safe_edit(
        query,
        welcome_message(user.first_name),
        reply_markup=main_menu_keyboard(),
    )


@authorized_only
async def go_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'go_back' callback — return to main menu (generic back)."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    # Clean up inactive tunnel on back
    from bot.services.cam_service import cam_service
    if not cam_service.is_running:
        session = get_session(user.id)
        tunnel_service = session.get('tunnel_service')
        if tunnel_service and tunnel_service.is_running():
            try:
                tunnel_service.stop_tunnel()
            except Exception:
                pass

    clear_conversation_state(user.id)
    context.user_data.clear()

    await _safe_edit(
        query,
        welcome_message(user.first_name),
        reply_markup=main_menu_keyboard(),
    )


@authorized_only
async def go_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'go_cancel' callback — cancel and return to menu."""
    query = update.callback_query
    await query.answer("Operation cancelled")

    user = update.effective_user

    # Clean up inactive tunnel on cancel callback
    from bot.services.cam_service import cam_service
    if not cam_service.is_running:
        session = get_session(user.id)
        tunnel_service = session.get('tunnel_service')
        if tunnel_service and tunnel_service.is_running():
            try:
                tunnel_service.stop_tunnel()
            except Exception:
                pass

    clear_conversation_state(user.id)
    context.user_data.clear()

    await _safe_edit(
        query,
        operation_cancelled(),
        reply_markup=main_menu_keyboard(),
    )


@authorized_only
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'menu_help' callback — show help from menu."""
    query = update.callback_query
    await query.answer()

    await _safe_edit(
        query,
        help_message(),
        reply_markup=home_only_keyboard(),
    )


@authorized_only
async def tunnel_control_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle tunnel control callbacks: restart, stop, show_url."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    session = get_session(user_id)
    tunnel_service = session.get('tunnel_service')

    if not tunnel_service:
        await query.edit_message_text("❌ No tunnel service found. Use /start to initialize.")
        return

    action = query.data

    if action == "restart_tunnel":
        try:
            tunnel_service.restart_tunnel()
            status = tunnel_service.get_status()
            msg = (
                f"✅ <b>Tunnel Restarted</b>\n\n"
                f"<b>URL:</b> <code>{status.get('url', 'N/A')}</code>\n"
                f"<b>Masked:</b> <code>{status.get('masked_url', 'N/A')}</code>\n"
                f"<b>Started:</b> {status.get('start_time', 'N/A')}\n"
            )
            await query.edit_message_text(msg, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error restarting tunnel: {e}")
            await query.edit_message_text(f"❌ Error restarting tunnel: {e}")

    elif action == "stop_tunnel":
        try:
            if tunnel_service.stop_tunnel():
                await query.edit_message_text("✅ Tunnel stopped successfully.")
            else:
                await query.edit_message_text("❌ Failed to stop tunnel.")
        except Exception as e:
            logger.error(f"Error stopping tunnel: {e}")
            await query.edit_message_text(f"❌ Error stopping tunnel: {e}")

    elif action == "show_url":
        status = tunnel_service.get_status()
        if status.get('running'):
            msg = (
                f"<b>🌐 Tunnel Information</b>\n\n"
                f"<b>Status:</b> ✅ Running\n"
                f"<b>URL:</b> <code>{status.get('url', 'N/A')}</code>\n"
                f"<b>Masked URL:</b> <code>{status.get('masked_url', 'N/A')}</code>\n"
                f"<b>Duration:</b> {status.get('duration', 'N/A')}\n"
            )
            await query.edit_message_text(msg, parse_mode="HTML")
        else:
            await query.edit_message_text("❌ No active tunnel running.")


# ── Also handle the callback from the SECOND start.py version's pattern ──
@authorized_only
async def legacy_tunnel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle legacy tunnel callback patterns from old menu code."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    session = get_session(user_id)
    tunnel_service = session.get('tunnel_service')

    if not tunnel_service:
        await query.edit_message_text("❌ No tunnel service found.")
        return

    action = query.data

    if action == "restart_tunnel":
        try:
            tunnel_service.restart_tunnel()
            status = tunnel_service.get_status()
            await query.edit_message_text(
                f"✅ Tunnel restarted!\nURL: {status.get('url', 'N/A')}\nMasked: {status.get('masked_url', 'N/A')}",
                reply_markup=query.message.reply_markup
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}")

    elif action == "stop_tunnel":
        if tunnel_service.stop_tunnel():
            await query.edit_message_text("✅ Tunnel stopped.", reply_markup=None)
        else:
            await query.edit_message_text("❌ Failed to stop tunnel.")

    elif action == "show_url":
        status = tunnel_service.get_status()
        if status.get('running'):
            await query.edit_message_text(
                f"🌐 URL: {status.get('url', 'N/A')}\nMasked: {status.get('masked_url', 'N/A')}\nStatus: Running\nDuration: {status.get('duration', 'N/A')}",
                reply_markup=query.message.reply_markup
            )
        else:
            await query.edit_message_text("❌ No active tunnel.")


def get_handlers():
    """Return all handlers for this module."""
    return [
        CommandHandler("start", start_command),
        CommandHandler("help", help_command),
        CommandHandler("myid", myid_command),
        CommandHandler("cancel", cancel_command),
        # Navigation callbacks
        CallbackQueryHandler(go_home_callback, pattern="^go_home$"),
        CallbackQueryHandler(go_back_callback, pattern="^go_back$"),
        CallbackQueryHandler(go_cancel_callback, pattern="^go_cancel$"),
        CallbackQueryHandler(help_callback, pattern="^menu_help$"),
        # Tunnel control callbacks (new style)
        CallbackQueryHandler(tunnel_control_callback, pattern="^(restart_tunnel|stop_tunnel|show_url)$"),
    ]