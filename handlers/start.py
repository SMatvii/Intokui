import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.messages import START_MESSAGE, HELP_MESSAGE
from utils.keyboards import get_main_menu_keyboard
from database.database import add_user

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    add_user(user.id, user.username or user.first_name)
    
    await update.message.reply_text(
        START_MESSAGE,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='HTML'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        HELP_MESSAGE,
        parse_mode='HTML'
    )


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("main_", "")
    
    if data == "habits":
        await show_habits_callback(query)
    elif data == "progress":
        await show_progress_callback(query)
    elif data == "stats":
        await show_detailed_stats_callback(query)


async def show_habits_callback(query):
    class FakeUpdate:
        def __init__(self, query):
            self.effective_user = query.from_user
            self.message = query.message
    
    fake_update = FakeUpdate(query)
    from handlers.habits import show_habits
    await show_habits(fake_update, None)


async def show_progress_callback(query):
    class FakeUpdate:
        def __init__(self, query):
            self.effective_user = query.from_user
            self.message = query.message
    
    fake_update = FakeUpdate(query)
    from handlers.stats import show_progress
    await show_progress(fake_update, None)


async def show_detailed_stats_callback(query):
    class FakeUpdate:
        def __init__(self, query):
            self.effective_user = query.from_user
            self.message = query.message
    
    fake_update = FakeUpdate(query)
    from handlers.stats import show_detailed_stats
    await show_detailed_stats(fake_update, None)
