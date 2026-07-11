"""
CyberAI Bot — URL Masker Handler
Multi-step conversational flow for masking URLs via Telegram.
"""

import logging
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, MessageHandler, filters
)

from bot.middleware.auth import authorized_only
from bot.utils.keyboards import (
    main_menu_keyboard, mask_result_keyboard, back_home_keyboard
)
from bot.utils.messages import (
    masker_prompt_url, masker_prompt_domain, masker_prompt_keywords,
    masker_processing, masker_result, masker_failed, error_message
)
from bot.services.masker_service import masker_service
from bot.database.session import (
    set_conversation_state, get_conversation_state,
    clear_conversation_state, log_activity
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


# ── Menu Entry ────────────────────────────────────────────────

@authorized_only
async def masker_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: user taps '🔗 URL Masker'."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    set_conversation_state(user.id, {"flow": "masker", "step": "url"})

    await _safe_edit(
        query,
        masker_prompt_url(),
        reply_markup=back_home_keyboard(),
    )


# ── Text Input Handler ───────────────────────────────────────

@authorized_only
async def masker_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text inputs during URL masker flow."""
    user = update.effective_user
    state = get_conversation_state(user.id)

    if state.get("flow") != "masker":
        return  # Not in masker flow

    step = state.get("step")
    text = update.message.text.strip()

    if step == "url":
        # Validate URL
        normalized, err = masker_service.validate_and_normalize(text)

        if err:
            await update.message.reply_text(
                f"{err}\n\nPlease enter a valid URL:",
            )
            return

        context.user_data["masker_url"] = normalized
        set_conversation_state(user.id, {"flow": "masker", "step": "domain"})

        await update.message.reply_text(
            f"URL validated: {normalized}\n\n" + masker_prompt_domain(),
            parse_mode="HTML",
            reply_markup=back_home_keyboard(),
        )

    elif step == "domain":
        # Store mask domain
        domain = text.replace("https://", "").replace("http://", "").strip()

        if not domain:
            await update.message.reply_text(
                "Please enter a valid domain name.",
            )
            return

        context.user_data["masker_domain"] = domain
        set_conversation_state(user.id, {"flow": "masker", "step": "keywords"})

        await update.message.reply_text(
            masker_prompt_keywords(),
            parse_mode="HTML",
        )

    elif step == "keywords":
        # Handle keywords (or /skip)
        keywords = "" if text.lower() in ("/skip", "skip") else text
        context.user_data["masker_keywords"] = keywords

        # Process the masking
        await _process_masking(update, context)


async def _process_masking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the URL masking."""
    user = update.effective_user
    original_url = context.user_data.get("masker_url", "")
    mask_domain = context.user_data.get("masker_domain", "")
    keywords = context.user_data.get("masker_keywords", "")

    # Send processing message
    processing_msg = await update.message.reply_text(
        masker_processing(),
        parse_mode="HTML",
    )

    # Perform masking
    result = await masker_service.mask_url(original_url, mask_domain, keywords)

    if result["success"]:
        text = masker_result(
            result["original_url"],
            result["shortened_url"],
            result["masked_urls"],
        )
        log_activity(user.id, "url_mask", f"url={original_url}, domain={mask_domain}")

        try:
            await processing_msg.edit_text(
                text,
                parse_mode="HTML",
                reply_markup=mask_result_keyboard(),
            )
        except BadRequest:
            # If edit fails, send a new message
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                parse_mode="HTML",
                reply_markup=mask_result_keyboard(),
            )
    else:
        try:
            await processing_msg.edit_text(
                masker_failed(result.get("error", "Unknown error")),
                parse_mode="HTML",
                reply_markup=mask_result_keyboard(),
            )
        except BadRequest:
            pass

    # Clear conversation state
    clear_conversation_state(user.id)


def get_handlers():
    """Return all handlers for this module."""
    return [
        CallbackQueryHandler(masker_menu_callback, pattern="^menu_masker$"),
    ]
