from telegram import Update
from telegram.ext import ContextTypes


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
        parsed_transaction = parser.parse(update.message.text)
        escaped_message = (
            repr(parsed_transaction) if is_debug else str(parsed_transaction)
        ).replace("[", r"\[")
        await update.message.reply_markdown(escaped_message)
    except ValueError as e:
        await update.message.reply_markdown(f"*⚠️ Error*: {e}")
