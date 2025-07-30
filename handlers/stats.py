import logging
from telegram import Update
from telegram.ext import ContextTypes

from database.database import get_user_total_stats, get_user_habits, get_habit_stats
from utils.keyboards import get_stats_keyboard

logger = logging.getLogger(__name__)


async def show_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habits = get_user_habits(user_id)
    
    if not habits:
        await update.message.reply_text(
            "У вас поки немає звичок для відстеження.\n"
            "Додайте першу звичку командою /add_habit"
        )
        return
    
    text = "Ваш прогрес сьогодні:\n\n"
    
    for habit in habits:
        stats = get_habit_stats(habit.id)
        text += f"{habit.name}\n"
        text += f"   Серія: {stats['streak']} днів\n"
        text += f"   Заощаджено: {stats['money_saved']:.2f} грн\n\n"
    
    total_stats = get_user_total_stats(user_id)
    text += f"Загальна економія: {total_stats['total_money_saved']:.2f} грн\n"
    text += f"Загальний успіх: {total_stats['average_success_rate']:.1f}%"
    
    await update.message.reply_text(text, parse_mode='HTML')


async def show_detailed_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    total_stats = get_user_total_stats(user_id)
    
    if total_stats['total_habits'] == 0:
        await update.message.reply_text(
            "У вас поки немає статистики.\n"
            "Додайте звички та почніть відстежувати свій прогрес!"
        )
        return
    
    text = "Детальна статистика\n\n"
    text += f"Всього звичок: {total_stats['total_habits']}\n"
    text += f"Днів відстеження: {total_stats['total_tracked_days']}\n"
    text += f"Чистих днів: {total_stats['total_clean_days']}\n"
    text += f"Загальна економія: {total_stats['total_money_saved']:.2f} грн\n"
    text += f"Середній успіх: {total_stats['average_success_rate']:.1f}%\n\n"
    
    if total_stats['average_success_rate'] >= 80:
        text += "Відмінний результат! Продовжуйте в тому ж дусі!"
    elif total_stats['average_success_rate'] >= 60:
        text += "Хороший прогрес! Ви на правильному шляху!"
    elif total_stats['average_success_rate'] >= 40:
        text += "Не здавайтесь! Кожен день - нова можливість!"
    else:
        text += "Початок завжди важкий. Головне не зупинятись!"
    
    keyboard = get_stats_keyboard()
    
    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )


async def handle_stats_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("stats_", "")
    
    if data == "weekly":
        await show_weekly_stats(query)
    elif data == "monthly":
        await show_monthly_stats(query)
    elif data == "achievements":
        await show_achievements(query)
    elif data == "charts":
        await show_charts(query)


async def show_weekly_stats(query):
    await query.edit_message_text(
        "Статистика за тиждень\n\n"
        "Ця функція буде додана в наступному оновленні."
    )


async def show_monthly_stats(query):
    await query.edit_message_text(
        "Статистика за місяць\n\n"
        "Ця функція буде додана в наступному оновленні."
    )


async def show_achievements(query):
    await query.edit_message_text(
        "Ваші досягнення\n\n"
        "Ця функція буде додана в наступному оновленні."
    )


async def show_charts(query):
    await query.edit_message_text(
        "Графіки прогресу\n\n"
        "Ця функція буде додана в наступному оновленні."
    )
