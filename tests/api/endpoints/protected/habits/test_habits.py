from datetime import datetime
from typing import List
from fastapi.testclient import TestClient
from pytest import Session

from app.models.models import Habit, HabitLog
from app.schemas.habit import (
    HabitCreateInput,
    HabitPublic,
    HabitWithLog,
)


def test_create_habit(
    client: TestClient,
    session: Session,
    habit_data: HabitCreateInput,
    access_token_headers: dict[str, str],
):
    response = client.post(
        "/habits",
        json=habit_data.dict(),
        headers=access_token_headers,
    )

    response_data = HabitPublic(**response.json())

    assert response.status_code == 201

    assert response_data.title == habit_data.title
    assert response_data.start_time_minutes == habit_data.start_time_minutes
    assert response_data.end_time_minutes == habit_data.end_time_minutes
    assert response_data.repeat_time_minutes == habit_data.repeat_time_minutes
    assert response_data.repeat_days == habit_data.repeat_days

    assert session.query(Habit).filter(Habit.id == response_data.id).first()


def test_get_habits(
    client: TestClient,
    session: Session,
    add_habit_list: list[Habit],
    add_habit_log_list: list[HabitLog],
    access_token_headers: dict[str, str],
):
    params = dict(
        limit=3,
        log_target_date="2024-06-12",
    )
    response = client.get(
        "/habits",
        headers=access_token_headers,
        params=params,
    )

    response_data: List[HabitWithLog] = [
        HabitWithLog(**habit) for habit in response.json()
    ]

    assert response.status_code == 200

    assert len(response_data) == 3
    assert response_data[0].id == 5
    assert response_data[1].id == 4
    assert response_data[2].id == 3
    assert response_data[0].near_weekday is not None

    assert len(response_data[0].log_list) == 0
    assert len(response_data[1].log_list) == 0
    assert len(response_data[2].log_list) == 0


def test_get_habits_valid_last_id(
    client: TestClient,
    session: Session,
    add_habit_list: list[Habit],
    add_habit_log_list: list[HabitLog],
    access_token_headers: dict[str, str],
):
    params = dict(
        limit=3,
        last_id=3,
        log_target_date="2024-06-12",
    )
    response = client.get(
        "/habits",
        headers=access_token_headers,
        params=params,
    )

    response_data: List[HabitWithLog] = [
        HabitWithLog(**habit) for habit in response.json()
    ]

    assert response.status_code == 200

    assert len(response_data) == 2

    assert response_data[0].id == 2
    assert response_data[1].id == 1

    assert len(response_data[0].log_list) == 5
    assert len(response_data[1].log_list) == 5

    assert response_data[0].log_list[0].completed_at == datetime(
        2024, 6, 12, 18, 0, 0
    )
    assert response_data[1].log_list[0].completed_at == datetime(
        2024, 6, 12, 13, 0, 0
    )

    assert response_data[0].log_list[0].id == 10
    assert response_data[1].log_list[0].id == 5


def test_get_habits_empty_log_date(
    client: TestClient,
    session: Session,
    add_habit_list: list[Habit],
    add_habit_log_list: list[HabitLog],
    access_token_headers: dict[str, str],
):
    params = dict(
        limit=3,
        log_target_date="2024-06-15",
    )
    response = client.get(
        "/habits",
        headers=access_token_headers,
        params=params,
    )

    response_data: List[HabitWithLog] = [
        HabitWithLog(**habit) for habit in response.json()
    ]

    assert response.status_code == 200

    assert len(response_data) == 3

    assert response_data[0].id == 5
    assert response_data[1].id == 4
    assert response_data[2].id == 3

    assert len(response_data[0].log_list) == 0
    assert len(response_data[1].log_list) == 0
    assert len(response_data[2].log_list) == 0


def test_get_habits_deactivated_habits(
    client: TestClient,
    session: Session,
    add_habit_list: list[Habit],
    add_habit_log_list: list[HabitLog],
    access_token_headers: dict[str, str],
):
    params = dict(
        limit=3,
        log_target_date="2024-06-15",
        activated=False,
    )
    response = client.get(
        "/habits",
        headers=access_token_headers,
        params=params,
    )

    response_data: List[HabitWithLog] = [
        HabitWithLog(**habit) for habit in response.json()
    ]

    assert response.status_code == 200

    assert len(response_data) == 1

    assert response_data[0].id == 6

    assert len(response_data[0].log_list) == 0


def test_delete_habit(
    client: TestClient,
    session: Session,
    add_habit_list: list[Habit],
    add_habit_log_list: list[HabitLog],
    access_token_headers: dict[str, str],
):
    response = client.delete(
        "/habits/1",
        headers=access_token_headers,
    )

    assert response.status_code == 204

    assert session.query(Habit).filter(Habit.id == 1).first() is None
    assert (
        session.query(HabitLog).filter(HabitLog.habit_id == 1).first() is None
    )


def test_delete_habit_not_found(
    client: TestClient,
    session: Session,
    access_token_headers: dict[str, str],
):
    response = client.delete(
        "/habits/1",
        headers=access_token_headers,
    )

    assert response.status_code == 404


def test_update_habit(
    client: TestClient,
    session: Session,
    access_token_headers: dict[str, str],
    add_habit_list: list[Habit],
):
    body = dict(
        title="changed",
        start_time_minutes=0,
        end_time_minutes=1440,
        repeat_time_minutes=60,
        repeat_days=[0, 1, 2, 3, 4],
        activated=False,
    )

    response = client.put(
        "/habits/1",
        headers=access_token_headers,
        json=body,
    )

    habit = session.query(Habit).filter(Habit.id == 1).first()

    assert response.status_code == 200
    assert habit.end_time_minutes == body["end_time_minutes"]
    assert habit.start_time_minutes == body["start_time_minutes"]
    assert habit.repeat_days == "01234"
    assert habit.repeat_time_minutes == body["repeat_time_minutes"]
    assert habit.activated == body["activated"]


def test_achieve_habit(
    client: TestClient,
    session: Session,
    access_token_headers: dict[str, str],
    add_habit_list: list[Habit],
):
    response = client.post(
        "/habits/achieve/1",
        headers=access_token_headers,
    )

    data = response.json()

    habit = session.query(HabitLog).filter(Habit.id == 1).first()

    assert response.status_code == 200
    assert data["completed_at"] is not None
    assert data["id"] == 1
    assert habit.habit_id == 1
