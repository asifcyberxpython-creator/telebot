"""
CyberAI Bot — Authentication Middleware
Decorator-based authorization for handler functions.
"""

import functools
import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.config import ADMIN_IDS, OPEN_REGISTRATION, DATA_DIR
from bot.utils.messages import unauthorized_message

logger = logging.getLogger(__name__)

# Runtime admin list (starts from config, can be extended)
_runtime_admins = set(ADMIN_IDS)


def add_admin(user_id: int):
    """Add a user ID to the runtime admin list."""
    _runtime_admins.add(user_id)
    logger.info(f"Admin added: {user_id}")


def is_admin(user_id: int) -> bool:
    """Check if a user ID is an admin."""
    if OPEN_REGISTRATION and not _runtime_admins:
        return True  # no admins configured, allow everyone until first registration
    return user_id in _runtime_admins


def authorized_only(func):
    """
    Decorator: restricts handler to authorized admin users only.
    If ADMIN_IDS is empty (open registration), the first user to interact
    becomes admin automatically.
    """
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user:
            return

        user_id = user.id

        # Open registration: first user becomes admin
        if OPEN_REGISTRATION and not _runtime_admins:
            add_admin(user_id)
            logger.info(f"First user registered as admin: {user_id} ({user.username})")

        if not is_admin(user_id):
            logger.warning(f"Unauthorized access attempt: {user_id} ({user.username})")

            if update.callback_query:
                await update.callback_query.answer("🚫 Unauthorized", show_alert=True)
            elif update.message:
                await update.message.reply_text(
                    unauthorized_message(),
                    parse_mode="HTML"
                )
            return

        return await func(update, context, *args, **kwargs)

    return wrapper
