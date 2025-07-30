import logging
import os
from dotenv import load_dotenv

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

from database.database import init_database
from handlers import start, habits, stats

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("BOT_TOKEN не знайдено в змінних середовища!")
        logger.error("Перевірте що файл .env існує та містить:")
        logger.error("BOT_TOKEN=ваш_токен_тут")
        return

    if token == "your_telegram_bot_token_here":
        logger.error("Замініть BOT_TOKEN на реальний токен від @BotFather")
        return

    init_database()

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start.start_command))
    application.add_handler(CommandHandler("help", start.help_command))
    application.add_handler(CommandHandler("habits", habits.show_habits))
    application.add_handler(CommandHandler("progress", stats.show_progress))
    application.add_handler(CommandHandler("stats", stats.show_detailed_stats))
    application.add_handler(CommandHandler("goals", habits.set_goals))
    add_habit_conv = ConversationHandler(
        entry_points=[CommandHandler("add_habit", habits.add_habit_start)],
        states={
            habits.HABIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, habits.get_habit_name)],
            habits.HABIT_COST: [MessageHandler(filters.TEXT & ~filters.COMMAND, habits.get_habit_cost)],
            habits.HABIT_FREQUENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, habits.get_habit_frequency)],
        },
        fallbacks=[CommandHandler("cancel", habits.cancel_add_habit)],
    )
    application.add_handler(add_habit_conv)
    application.add_handler(CallbackQueryHandler(start.handle_main_menu, pattern="^main_"))
    application.add_handler(CallbackQueryHandler(habits.handle_habit_action, pattern="^habit_"))
    application.add_handler(CallbackQueryHandler(stats.handle_stats_action, pattern="^stats_"))

    logger.info("Бот запущено успішно!")
    
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == '__main__':
    main()
