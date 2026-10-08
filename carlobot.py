import logging

from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PersistenceInput,
    PicklePersistence,
    filters,
)

import environment
from message_parser import MessageParser, TransactionType

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def debug_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    is_debug = not context.user_data.get("debug", False)
    context.user_data["debug"] = is_debug
    await update.message.reply_text(f"Debug mode {'on' if is_debug else 'off'}")


async def transaction_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    parser = MessageParser()

    answer, type = parser.transaction_type(update.message.text)
    is_debug = context.user_data.get("debug", False)

    debug_info = f"*Choice:* {answer.choice}\n*Confidence:* {answer.confidence}"
    reply_message = (
        "*⚠️ Error*: Not a transaction"
        if type == TransactionType.NONE
        else f"*Type:* {type.name.capitalize()}"
    )

    await update.message.reply_markdown(
        f"{reply_message}\n{debug_info}" if is_debug else reply_message
    )


def main() -> None:
    persistence = PicklePersistence(
        filepath="persistence",
        store_data=PersistenceInput(
            chat_data=True, bot_data=False, user_data=True, callback_data=False
        ),
    )
    application = (
        Application.builder()
        .token(environment.TG_BOT_TOKEN)
        .persistence(persistence=persistence)
        .build()
    )

    application.add_handler(CommandHandler("debug", debug_mode))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, transaction_type)
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
