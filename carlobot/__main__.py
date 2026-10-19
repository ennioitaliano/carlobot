from telegram import Update

from carlobot.bot.app import create_application


def main() -> None:
    application = create_application()
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
