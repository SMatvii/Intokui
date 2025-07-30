from datetime import datetime, timedelta
import random
from utils.messages import MOTIVATIONAL_MESSAGES


def calculate_streak(logs):
    if not logs:
        return 0
    
    streak = 0
    for log in reversed(logs):
        if not log.did_habit:
            streak += 1
        else:
            break
    
    return streak


def calculate_money_saved(habit, clean_days):
    return habit.cost_per_day * clean_days


def calculate_success_rate(total_days, clean_days):
    if total_days == 0:
        return 0
    return (clean_days / total_days) * 100


def get_motivational_message():
    return random.choice(MOTIVATIONAL_MESSAGES)


def format_duration(days):
    if days == 0:
        return "0 днів"
    elif days == 1:
        return "1 день"
    elif days < 5:
        return f"{days} дні"
    else:
        return f"{days} днів"


def get_achievement_level(streak):
    from config import ACHIEVEMENT_MILESTONES
    
    for milestone in reversed(ACHIEVEMENT_MILESTONES):
        if streak >= milestone:
            return milestone
    return 0


def format_money(amount):
    return f"{amount:.2f} грн"


def is_today(date):
    today = datetime.now().date()
    return date.date() == today


def get_week_start():
    today = datetime.now()
    start = today - timedelta(days=today.weekday())
    return start.replace(hour=0, minute=0, second=0, microsecond=0)


def get_month_start():
    today = datetime.now()
    return today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
