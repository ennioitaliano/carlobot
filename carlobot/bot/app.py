import asyncio
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
from carlobot.categories.builder import CategoriesBuilder
from carlobot.domain import TransactionType
from carlobot.services.parser import MessageParser
from carlobot.sheets.writer import SheetWriter

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def _build_categories(app: Application) -> None:
    builder = CategoriesBuilder()
    await builder.write_categories()

    exp_data = builder.get_categories(TransactionType.EXPENSE)
    inc_data = builder.get_categories(TransactionType.INCOME)

    app.bot_data["parser"] = MessageParser(exp_data, inc_data)


async def post_init(application: Application) -> None:

    application.bot_data["sheet_writer"] = SheetWriter()

    exp_file = config.CATEGORIES_CACHE_DIR / "exp_cat.json"
    inc_file = config.CATEGORIES_CACHE_DIR / "inc_cat.json"

    if exp_file.exists() and inc_file.exists():
        builder = CategoriesBuilder()
        exp_data = builder.get_categories(TransactionType.EXPENSE)
        inc_data = builder.get_categories(TransactionType.INCOME)
        application.bot_data["parser"] = MessageParser(exp_data, inc_data)
    else:
        asyncio.create_task(_build_categories(application))

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

    application.bot_data["parser"] = None

    application.add_handler(CommandHandler("debug", debug_mode))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, parse_message)
    )

    return application
