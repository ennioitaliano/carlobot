import asyncio
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

logger = logging.getLogger(__name__)


async def debug_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    is_debug = not context.user_data.get("debug", False)
    context.user_data["debug"] = is_debug
    if update.message:
        await update.message.reply_text(f"Debug mode {'on' if is_debug else 'off'}")


async def parse_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    parser = context.bot_data["parser"]
    is_debug = context.user_data.get("debug", False)

    if not parser:
        return

    try:
        status_message = await update.message.reply_markdown("_Parsing message..._")

        parsed_transaction = parser.parse(update.message.text)
        escaped_message = (
            repr(parsed_transaction) if is_debug else str(parsed_transaction)
        ).replace("[", r"\[")
        await status_message.edit_text(
            escaped_message + "\n_Writing to Google Sheets..._",
            parse_mode=ParseMode.MARKDOWN,
        )

        writer = context.bot_data["sheet_writer"]
        await asyncio.to_thread(writer.write_values, parsed_transaction)

        await status_message.edit_text(
            escaped_message + "\n✅ Written to Google Sheets",
            parse_mode=ParseMode.MARKDOWN,
        )

    except Exception as e:
        logger.exception("Failed to process transaction")
        error_text = escape_markdown(str(e), version=1)
        await update.message.reply_markdown(f"*⚠️ Error*: {error_text}")
