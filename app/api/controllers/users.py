from contextlib import contextmanager
from fastapi import APIRouter, Depends, status

from app.core.auth import get_current_user
from ..dao import get_user_dao
from ..dao.user_dao import UserDAO
from app.database.db import tx_manager
from app.models.models import User

from app.schemas.user import UserData, UserUpdateInput

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/me",
    response_model=UserData,
    status_code=status.HTTP_200_OK,
    operation_id="getMe",
)
def get_me(user: User = Depends(get_current_user)):
    return UserData.from_orm(user)


@router.put(
    "/me",
    response_model=UserData,
    status_code=status.HTTP_200_OK,
    operation_id="updateMe",
)
def update_me(
    data: UserUpdateInput,
    user=Depends(get_current_user),
    user_dao: UserDAO = Depends(get_user_dao),
    tx_manager: contextmanager = Depends(tx_manager),
):
    with tx_manager:
        user = user_dao.update_me(data)

    return UserData.from_orm(user)
