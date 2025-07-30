import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from database.database import add_habit, get_user_habits, log_habit_activity, get_habit_stats
from utils.messages import ADD_HABIT_MESSAGES, HABIT_MESSAGES
from utils.keyboards import get_habits_keyboard, get_habit_actions_keyboard

logger = logging.getLogger(__name__)

HABIT_NAME, HABIT_COST, HABIT_FREQUENCY = range(3)


async def show_habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habits = get_user_habits(user_id)
    
    if not habits:
        await update.message.reply_text(
            "У вас поки немає збережених звичок.\n"
            "Використайте команду /add_habit щоб додати першу звичку!"
        )
        return
    
    text = "Ваші шкідливі звички:\n\n"
    
    for habit in habits:
        stats = get_habit_stats(habit.id)
        text += f"• {habit.name}\n"
        text += f"  Вартість: {habit.cost_per_day} грн/день\n"
        text += f"  Поточна серія: {stats['streak']} днів\n"
        text += f"  Заощаджено: {stats['money_saved']:.2f} грн\n\n"
    
    keyboard = get_habits_keyboard(habits)
    
    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )


async def add_habit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ADD_HABIT_MESSAGES['name'])
    return HABIT_NAME


async def get_habit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['habit_name'] = update.message.text
    await update.message.reply_text(ADD_HABIT_MESSAGES['cost'])
    return HABIT_COST


async def get_habit_cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cost = float(update.message.text)
        context.user_data['habit_cost'] = cost
        await update.message.reply_text(ADD_HABIT_MESSAGES['frequency'])
        return HABIT_FREQUENCY
    except ValueError:
        await update.message.reply_text(
            "Будь ласка, введіть правильну суму (наприклад: 50 або 100.5)"
        )
        return HABIT_COST


async def get_habit_frequency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        frequency = int(update.message.text)
        
        habit = add_habit(
            user_id=update.effective_user.id,
            name=context.user_data['habit_name'],
            cost_per_day=context.user_data['habit_cost'],
            frequency_per_day=frequency
        )
        
        await update.message.reply_text(
            f"Звичку додано успішно!\n\n"
            f"Назва: {habit.name}\n"
            f"Вартість: {habit.cost_per_day} грн/день\n"
            f"Частота: {habit.frequency_per_day} разів/день\n"
            f"Ціль: {habit.goal_days} днів без звички\n\n"
            f"Тепер ви можете відстежувати свій прогрес!",
            parse_mode='HTML'
        )
        
        context.user_data.clear()
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "Будь ласка, введіть правильне число (наприклад: 1, 5, 10)"
        )
        return HABIT_FREQUENCY


async def cancel_add_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Додавання звички скасовано.")
    return ConversationHandler.END


async def handle_habit_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("habit_", "")
    
    if data.startswith("view_"):
        habit_id = int(data.replace("view_", ""))
        await show_habit_details(query, habit_id)
    elif data.startswith("did_"):
        habit_id = int(data.replace("did_", ""))
        await log_habit_did(query, habit_id)
    elif data.startswith("clean_"):
        habit_id = int(data.replace("clean_", ""))
        await log_habit_clean(query, habit_id)
    elif data == "add":
        await query.edit_message_text(
            "Для додавання нової звички використайте команду /add_habit"
        )


async def show_habit_details(query, habit_id: int):
    habits = get_user_habits(query.from_user.id)
    habit = next((h for h in habits if h.id == habit_id), None)
    
    if not habit:
        await query.edit_message_text("Звичку не знайдено")
        return
    
    stats = get_habit_stats(habit_id)
    
    text = f"Детальна статистика: {habit.name}\n\n"
    text += f"Вартість за день: {habit.cost_per_day} грн\n"
    text += f"Частота: {habit.frequency_per_day} разів/день\n"
    text += f"Ціль: {habit.goal_days} днів\n\n"
    text += f"Ваш прогрес:\n"
    text += f"Поточна серія: {stats['streak']} днів\n"
    text += f"Чистих днів: {stats['clean_days']}\n"
    text += f"Всього відстежується: {stats['total_days']} днів\n"
    text += f"Заощаджено грошей: {stats['money_saved']:.2f} грн\n"
    text += f"Рівень успіху: {stats['success_rate']:.1f}%\n\n"
    text += "Що ви робили сьогодні?"
    
    keyboard = get_habit_actions_keyboard(habit_id)
    
    await query.edit_message_text(
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )


async def log_habit_did(query, habit_id: int):
    success = log_habit_activity(habit_id, query.from_user.id, did_habit=True)
    
    if success:
        await query.edit_message_text(
            "Записано, що ви зробили звичку сьогодні.\n"
            "Не засмучуйтесь! Завтра новий день - нова можливість!"
        )
    else:
        await query.edit_message_text("Помилка при збереженні даних")


async def log_habit_clean(query, habit_id: int):
    success = log_habit_activity(habit_id, query.from_user.id, did_habit=False)
    
    if success:
        stats = get_habit_stats(habit_id)
        await query.edit_message_text(
            f"Відмінно! Ви утрималися від звички!\n"
            f"Ваша серія: {stats['streak']} днів\n"
            f"Заощаджено сьогодні: {stats['money_saved']:.2f} грн\n"
            f"Так тримати!"
        )
    else:
        await query.edit_message_text("Помилка при збереженні даних")


async def set_goals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Встановлення цілей\n\n"
        "Ця функція буде додана в наступному оновленні!\n"
        "Поки що ваша ціль - 30 днів без кожної звички.",
        parse_mode='HTML'
    )
