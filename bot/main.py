"""
CyberAI Bot — Application Builder
Wires up all handlers, middleware, and starts the Telegram bot.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

from telegram import Update
from telegram.error import BadRequest, Conflict, TimedOut, NetworkError
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from telegram.request import HTTPXRequest

from bot.config import BOT_TOKEN, LOG_LEVEL, LOG_FILE
from bot.handlers import start, cam_handler, masker_handler, logs_handler, settings_handler
from bot.database.session import get_conversation_state, SessionManager
from bot.services.tunnel_service import CloudflareTunnelService

load_dotenv()

# ── Logging Setup ─────────────────────────────────────────────

def setup_logging():
    """Configure logging for the bot."""
    log_format = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO"), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.getenv("LOG_FILE", "bot.log"), encoding='utf-8'),
        ],
    )

    # Quiet down some noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)


# ── Unified Text Handler ─────────────────────────────────────

async def unified_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    A single text handler that routes to the correct flow based on
    the user's current conversation state.

    This prevents conflicts between multiple MessageHandlers for TEXT.
    """
    user = update.effective_user
    if not user:
        return

    state = get_conversation_state(user.id)
    flow = state.get("flow", "")

    if flow == "cam_setup":
        from bot.handlers.cam_handler import cam_text_input
        await cam_text_input(update, context)

    elif flow == "masker":
        from bot.handlers.masker_handler import masker_text_input
        await masker_text_input(update, context)

    elif flow == "settings":
        from bot.handlers.settings_handler import settings_text_input
        await settings_text_input(update, context)

    else:
        # No active flow — show help hint
        await update.message.reply_text(
            "Use /start to open the main menu, or /help for commands.",
        )


# ── Error Handler ─────────────────────────────────────────────

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """
    Global error handler.
    Silently ignores known harmless errors:
    - Conflict (multiple bot instances — transient during restarts)
    - BadRequest for 'Message is not modified' (user double-tapped a button)
    - TimedOut / NetworkError (transient network issues)
    """
    error = context.error

    # ── Silently ignore harmless errors ──
    if isinstance(error, Conflict):
        logger.debug(f"Conflict (another instance): {error}")
        return

    if isinstance(error, BadRequest):
        msg = str(error).lower()
        if "message is not modified" in msg:
            logger.debug(f"Message not modified (harmless): {error}")
            return
        if "message to edit not found" in msg:
            logger.debug(f"Message to edit not found (harmless): {error}")
            return
        if "query is too old" in msg:
            logger.debug(f"Callback query too old (harmless): {error}")
            return

    if isinstance(error, (TimedOut, NetworkError)):
        logger.warning(f"Network issue (transient): {error}")
        return

    # ── Log real errors ──
    logger.error(f"Exception while handling update: {error}", exc_info=error)

    # Try to notify the user
    if isinstance(update, Update) and update.effective_chat:
        try:
            error_text = str(error)[:200]
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"⚠️ An unexpected error occurred.\n\n{error_text}\n\nPlease try again or use /start to restart.",
            )
        except Exception:
            pass


# ── Tunnel Service Management ─────────────────────────────────

async def initialize_tunnels(context: ContextTypes.DEFAULT_TYPE):
    """
    Initialize Cloudflare Tunnel services for all existing users.
    Runs once at startup.
    """
    logger.info("Initializing tunnel services for existing users...")
    try:
        for user_id in SessionManager.get_all_users():
            session = SessionManager.get_session(user_id)
            if 'tunnel_service' not in session or session['tunnel_service'] is None:
                session['tunnel_service'] = CloudflareTunnelService()
                SessionManager.save_session(user_id, session)
                logger.debug(f"Tunnel initialized for user {user_id}")
    except Exception as e:
        logger.error(f"Error initializing tunnels: {e}")


async def cleanup_tunnels(context: ContextTypes.DEFAULT_TYPE):
    """
    Cleanup all tunnel services on bot shutdown.
    """
    logger.info("Cleaning up tunnel services...")
    try:
        for user_id in SessionManager.get_all_users():
            session = SessionManager.get_session(user_id)
            tunnel_service = session.get('tunnel_service')
            if tunnel_service:
                try:
                    tunnel_service.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up tunnel for user {user_id}: {e}")
    except Exception as e:
        logger.error(f"Error during tunnel cleanup: {e}")


# ── Application Builder ──────────────────────────────────────

def build_application() -> Application:
    """Build and configure the Telegram bot application."""
    setup_logging()

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN is not set! Check your .env file.")

    logger.info("Building CyberAI Bot application...")

    # Use extended timeouts for slow/unstable connections
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )

    app = (
        Application.builder()
        .token(bot_token)
        .request(request)
        .build()
    )

    # ── Register Handlers ──
    # Order matters: specific handlers first, generic text handler last

    # 1. Start/navigation handlers
    for handler in start.get_handlers():
        app.add_handler(handler)

    # 2. Camera handler (callbacks + commands)
    for handler in cam_handler.get_handlers():
        app.add_handler(handler)

    # 3. Masker handler (callbacks + commands)
    for handler in masker_handler.get_handlers():
        app.add_handler(handler)

    # 4. Logs handler (callbacks + commands)
    for handler in logs_handler.get_handlers():
        app.add_handler(handler)

    # 5. Settings handler (callbacks + commands)
    for handler in settings_handler.get_handlers():
        app.add_handler(handler)

    # 6. Unified text handler (must be last to catch text inputs)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, unified_text_handler)
    )

    # 7. Error handler
    app.add_error_handler(error_handler)

    # ── Job Queue Setup ──
    if app.job_queue:
        # Initialize tunnels at startup
        app.job_queue.run_once(initialize_tunnels, when=0)

        # Register shutdown handler for tunnel cleanup
        app.job_queue.run_once(cleanup_tunnels, when=300)  # Fallback cleanup after 5 min
    else:
        logger.error("JobQueue is not initialized! Startup tunnel setup and cleanup fallback will be disabled.")

    logger.info("CyberAI Bot application built successfully")
    return app


PORT = int(os.environ.get("PORT", 5000))


def run():
    """
    Build and run the bot.
    - If RENDER_EXTERNAL_URL is set → webhook mode on 0.0.0.0:PORT  (for Render)
    - Otherwise → polling mode (for local development)
    """
    app = build_application()

    logger.info("=" * 50)
    logger.info("  CyberAI Bot Starting...")
    bot_username = os.getenv("BOT_USERNAME", "@telecyber_ai_bot")
    logger.info(f"  Bot: {bot_username}")
    logger.info("=" * 50)

    render_url = os.environ.get("RENDER_EXTERNAL_URL")

    if render_url:
        # ── Webhook mode (Render / production) ──
        webhook_url = f"{render_url}/{os.getenv('BOT_TOKEN')}"
        logger.info(f"  Mode: Webhook")
        logger.info(f"  Listening on 0.0.0.0:{PORT}")
        logger.info(f"  Webhook URL: {render_url}/***")

        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=os.getenv("BOT_TOKEN"),
            webhook_url=webhook_url,
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
        )
    else:
        # ── Polling mode (local development) ──
        logger.info("  Mode: Polling (local)")

        app.run_polling(
            drop_pending_updates=True,
            timeout=30,
            bootstrap_retries=5,
            allowed_updates=Update.ALL_TYPES,
        )


if __name__ == "__main__":
    run()
