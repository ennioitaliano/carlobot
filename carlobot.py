import logging

import telegram
from telegram import BotCommand, ForceReply, MenuButtonCommands, Update
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


async def parse_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    parser = MessageParser()
    is_debug = context.user_data.get("debug", False)

    try:
        parsed_transaction = parser.parse(update.message.text)
        escaped_message = (
            repr(parsed_transaction) if is_debug else str(parsed_transaction)
        ).replace("[", r"\[")
        await update.message.reply_markdown(escaped_message)
    except ValueError as e:
        await update.message.reply_markdown(f"*⚠️ Error*: {e}")


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            BotCommand("debug", "Toggle debug mode"),
        ]
    )
    await application.bot.set_chat_menu_button(menu_button=MenuButtonCommands())


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
        .persistence(persistence)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("debug", debug_mode))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, parse_message)
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
