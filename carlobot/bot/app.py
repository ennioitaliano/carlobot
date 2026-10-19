import logging

from telegram import BotCommand, MenuButtonCommands
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    PersistenceInput,
    PicklePersistence,
    filters,
)

from carlobot import config
from carlobot.bot.handlers import debug_mode, parse_message

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            BotCommand("debug", "Toggle debug mode"),
        ]
    )
    await application.bot.set_chat_menu_button(menu_button=MenuButtonCommands())


def create_application() -> Application:
    persistence = PicklePersistence(
        filepath=str(config.PERSISTENCE_PATH),
        store_data=PersistenceInput(
            chat_data=True, bot_data=False, user_data=True, callback_data=False
        ),
    )

    application = (
        Application.builder()
        .token(config.TG_BOT_TOKEN)
        .persistence(persistence)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("debug", debug_mode))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, parse_message)
    )

    return application
