from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship

from app.database.db import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    grade = Column(Integer, nullable=False)
    profile_image = Column(String(100))
    nickname = Column(String(50))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    todos = relationship("Todo", back_populates="user")
    habits = relationship("Habit", back_populates="user")
    routines = relationship("Routine", back_populates="user")


class Todo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(Text)
    completed = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)

    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="todos")


class Habit(Base):
    __tablename__ = "habit"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    start_time_minutes = Column(Integer, nullable=False)
    repeat_days = Column(Text, nullable=False)
    active = Column(Integer, default=0)
    deleted_at = Column(TIMESTAMP)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="habits")
    habit_logs = relationship("HabitLog", back_populates="habit")


class HabitLog(Base):
    __tablename__ = "habit_log"

    id = Column(Integer, primary_key=True)

    completed_at = Column(TIMESTAMP)

    habit_id = Column(
        Integer, ForeignKey("habit.id", ondelete="CASCADE"), nullable=False
    )
    habit = relationship("Habit", back_populates="habit_logs")


class Routine(Base):
    __tablename__ = "routine"

    id = Column(Integer, primary_key=True)

    title = Column(Text, nullable=False)
    start_time_minutes = Column(Integer, nullable=False)
    repeat_days = Column(Text, nullable=False)
    deleted_at = Column(TIMESTAMP)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="routines")
    routine_elements = relationship("RoutineElement", back_populates="routine")


class RoutineElement(Base):
    __tablename__ = "routine_element"

    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    duration_minutes = Column(Integer)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    deleted_at = Column(TIMESTAMP)

    routine_id = Column(
        Integer, ForeignKey("routine.id", ondelete="CASCADE"), nullable=False
    )
    routine = relationship("Routine", back_populates="routine_elements")
    routine_logs = relationship("RoutineLog", back_populates="routine_element")


class RoutineLog(Base):
    __tablename__ = "routine_log"

    id = Column(Integer, primary_key=True, autoincrement=True)

    completed_at = Column(TIMESTAMP)

    routine_element_id = Column(
        Integer, ForeignKey("routine_element.id"), nullable=False
    )

    routine_element = relationship(
        "RoutineElement", back_populates="routine_logs"
    )
