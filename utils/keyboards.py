from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List
from database.models import Habit


def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Мої звички", callback_data="main_habits")],
        [InlineKeyboardButton("Прогрес", callback_data="main_progress")],
        [InlineKeyboardButton("Статистика", callback_data="main_stats")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_habits_keyboard(habits: List[Habit]):
    keyboard = []
    
    for habit in habits:
        keyboard.append([
            InlineKeyboardButton(
                f"{habit.name}", 
                callback_data=f"habit_view_{habit.id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("Додати звичку", callback_data="habit_add")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_habit_actions_keyboard(habit_id: int):
    keyboard = [
        [
            InlineKeyboardButton("Зробив звичку", callback_data=f"habit_did_{habit_id}"),
            InlineKeyboardButton("Утримався", callback_data=f"habit_clean_{habit_id}")
        ],
        [InlineKeyboardButton("Статистика", callback_data=f"habit_stats_{habit_id}")],
        [InlineKeyboardButton("Назад", callback_data="main_habits")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_stats_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("За тиждень", callback_data="stats_weekly"),
            InlineKeyboardButton("За місяць", callback_data="stats_monthly")
        ],
        [InlineKeyboardButton("Досягнення", callback_data="stats_achievements")],
        [InlineKeyboardButton("Графіки", callback_data="stats_charts")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard(action: str, habit_id: int = None):
    callback_data = f"confirm_{action}"
    if habit_id:
        callback_data += f"_{habit_id}"
    
    keyboard = [
        [
            InlineKeyboardButton("Так", callback_data=callback_data + "_yes"),
            InlineKeyboardButton("Ні", callback_data=callback_data + "_no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
