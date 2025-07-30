import sqlite3
import logging
from datetime import datetime, date
from typing import List, Optional
from .models import User, Habit, HabitLog

logger = logging.getLogger(__name__)

def get_connection():
    return sqlite3.connect('habits.db')

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            cost_per_day REAL DEFAULT 0,
            frequency_per_day INTEGER DEFAULT 1,
            goal_days INTEGER DEFAULT 30,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER,
            user_id INTEGER,
            date DATE,
            did_habit BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(habit_id, date)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            habit_id INTEGER,
            goal_days INTEGER,
            start_date DATE,
            end_date DATE,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("База даних ініціалізована успішно")

def add_user(user_id: int, username: str = None) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO users (id, username) 
            VALUES (?, ?)
        ''', (user_id, username))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Помилка додавання користувача: {e}")
        return False

def add_habit(user_id: int, name: str, cost_per_day: float = 0, frequency_per_day: int = 1) -> Optional[Habit]:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO habits (user_id, name, cost_per_day, frequency_per_day)
            VALUES (?, ?, ?, ?)
        ''', (user_id, name, cost_per_day, frequency_per_day))
        
        habit_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return Habit(
            id=habit_id,
            user_id=user_id,
            name=name,
            cost_per_day=cost_per_day,
            frequency_per_day=frequency_per_day,
            goal_days=30,
            created_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"Помилка додавання звички: {e}")
        return None

def get_user_habits(user_id: int) -> List[Habit]:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, name, cost_per_day, frequency_per_day, goal_days, created_at
            FROM habits WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        habits = []
        for row in cursor.fetchall():
            habits.append(Habit(
                id=row[0],
                user_id=row[1],
                name=row[2],
                cost_per_day=row[3],
                frequency_per_day=row[4],
                goal_days=row[5],
                created_at=datetime.fromisoformat(row[6])
            ))
        
        conn.close()
        return habits
    except Exception as e:
        logger.error(f"Помилка отримання звичок: {e}")
        return []

def log_habit_activity(habit_id: int, user_id: int, did_habit: bool) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        today = date.today()
        
        cursor.execute('''
            INSERT OR REPLACE INTO habit_logs (habit_id, user_id, date, did_habit)
            VALUES (?, ?, ?, ?)
        ''', (habit_id, user_id, today, did_habit))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Помилка запису активності: {e}")
        return False

def get_habit_logs(habit_id: int) -> List[HabitLog]:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, habit_id, user_id, date, did_habit, created_at
            FROM habit_logs WHERE habit_id = ?
            ORDER BY date DESC
        ''', (habit_id,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append(HabitLog(
                id=row[0],
                habit_id=row[1],
                user_id=row[2],
                date=datetime.strptime(row[3], '%Y-%m-%d').date(),
                did_habit=bool(row[4]),
                created_at=datetime.fromisoformat(row[5])
            ))
        
        conn.close()
        return logs
    except Exception as e:
        logger.error(f"Помилка отримання логів: {e}")
        return []

def get_habit_stats(habit_id: int) -> dict:
    try:
        logs = get_habit_logs(habit_id)
        
        if not logs:
            return {
                'streak': 0,
                'clean_days': 0,
                'total_days': 0,
                'money_saved': 0.0,
                'success_rate': 0.0
            }
             
        streak = 0
        for log in logs:
            if not log.did_habit:
                streak += 1
            else:
                break
        
        clean_days = sum(1 for log in logs if not log.did_habit)
        total_days = len(logs)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT cost_per_day FROM habits WHERE id = ?', (habit_id,))
        cost_per_day = cursor.fetchone()[0] or 0
        conn.close()
        
        money_saved = clean_days * cost_per_day
        success_rate = (clean_days / total_days * 100) if total_days > 0 else 0
        
        return {
            'streak': streak,
            'clean_days': clean_days,
            'total_days': total_days,
            'money_saved': money_saved,
            'success_rate': success_rate
        }
    except Exception as e:
        logger.error(f"Помилка розрахунку статистики: {e}")
        return {
            'streak': 0,
            'clean_days': 0,
            'total_days': 0,
            'money_saved': 0.0,
            'success_rate': 0.0
        }

def get_user_total_stats(user_id: int) -> dict:
    try:
        habits = get_user_habits(user_id)
        
        if not habits:
            return {
                'total_habits': 0,
                'total_tracked_days': 0,
                'total_clean_days': 0,
                'total_money_saved': 0.0,
                'average_success_rate': 0.0
            }
        
        total_habits = len(habits)
        total_tracked_days = 0
        total_clean_days = 0
        total_money_saved = 0.0
        success_rates = []
        
        for habit in habits:
            stats = get_habit_stats(habit.id)
            total_tracked_days += stats['total_days']
            total_clean_days += stats['clean_days']
            total_money_saved += stats['money_saved']
            if stats['total_days'] > 0:
                success_rates.append(stats['success_rate'])
        
        average_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
        
        return {
            'total_habits': total_habits,
            'total_tracked_days': total_tracked_days,
            'total_clean_days': total_clean_days,
            'total_money_saved': total_money_saved,
            'average_success_rate': average_success_rate
        }
    except Exception as e:
        logger.error(f"Помилка отримання загальної статистики: {e}")
        return {
            'total_habits': 0,
            'total_tracked_days': 0,
            'total_clean_days': 0,
            'total_money_saved': 0.0,
            'average_success_rate': 0.0
        }
