import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_FILE = 'habits.db'

LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

DEFAULT_TIMEZONE = 'Europe/Kiev'

MAX_MESSAGE_LENGTH = 4096
ITEMS_PER_PAGE = 10

ACHIEVEMENT_MILESTONES = [1, 3, 7, 14, 30, 60, 90, 180, 365]

REMINDER_HOURS = [9, 18, 21]

HABIT_EMOJIS = {
    'smoking': 'Куріння',
    'alcohol': 'Алкоголь', 
    'sweets': 'Солодощі',
    'social_media': 'Соціальні мережі',
    'gambling': 'Азартні ігри',
    'coffee': 'Кава',
    'fast_food': 'Фастфуд',
    'gaming': 'Ігри',
    'shopping': 'Шопінг',
    'other': 'Інше'
}
