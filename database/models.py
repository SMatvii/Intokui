from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class User:
    id: int
    username: Optional[str]
    created_at: datetime


@dataclass
class Habit:
    id: int
    user_id: int
    name: str
    cost_per_day: float
    frequency_per_day: int
    goal_days: int
    created_at: datetime


@dataclass
class HabitLog:
    id: int
    habit_id: int
    user_id: int
    date: date
    did_habit: bool
    created_at: datetime


@dataclass
class UserGoal:
    id: int
    user_id: int
    habit_id: int
    goal_days: int
    start_date: date
    end_date: date
    completed: bool
    created_at: datetime
