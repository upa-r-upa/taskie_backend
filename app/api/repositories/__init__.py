from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.db import get_db
from app.models.models import User
from .habit_repository import HabitRepository
from .task_repository import TaskRepository
from .routine_repository import RoutineRepository


def get_routine_repository(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return RoutineRepository(db=db, user=user)


def get_habit_repository(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return HabitRepository(db=db, user=user)


def get_task_repository(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return TaskRepository(db=db, user=user)
