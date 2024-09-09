from contextlib import contextmanager
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.errors import DATA_DOES_NOT_EXIST
from app.core.auth import get_current_user
from app.database.db import tx_manager
from app.exceptions.exceptions import DataNotFoundError
from ..repositories import get_habit_repository
from ..repositories.habit_repository import HabitRepository
from app.schemas.habit import (
    HabitCreateInput,
    HabitDetail,
    HabitListGetParams,
    HabitWithLog,
)
from app.schemas.response import Response

router = APIRouter(
    prefix="/habits", tags=["habits"], dependencies=[Depends(get_current_user)]
)


@router.post(
    "",
    response_model=Response[HabitDetail],
    status_code=status.HTTP_201_CREATED,
    operation_id="createHabit",
)
def create_habit(
    data: HabitCreateInput,
    repository: HabitRepository = Depends(get_habit_repository),
    tx_manager: contextmanager = Depends(tx_manager),
):
    with tx_manager:
        habit = repository.create_habit(data)

    return Response(data=HabitDetail.from_orm(habit))


@router.get(
    "",
    response_model=Response[List[HabitWithLog]],
    status_code=status.HTTP_200_OK,
    operation_id="getHabitList",
)
def get_habits(
    params: HabitListGetParams = Depends(),
    repository: HabitRepository = Depends(get_habit_repository),
):
    habits_with_logs = repository.get_habits_with_date_logs(**params.dict())

    return Response(data=habits_with_logs)


@router.delete(
    "/{habit_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="deleteHabit",
)
def delete_habit(
    habit_id: int,
    repository: HabitRepository = Depends(get_habit_repository),
    tx_manager: contextmanager = Depends(tx_manager),
):
    with tx_manager:
        try:
            repository.delete_habit(
                habit_id=habit_id,
            )
        except DataNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=DATA_DOES_NOT_EXIST,
            )

    return None