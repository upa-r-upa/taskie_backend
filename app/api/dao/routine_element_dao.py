from fastapi import HTTPException, status
from sqlalchemy import asc

from .base import ProtectedBaseDAO
from app.api.errors import DATA_DOES_NOT_EXIST
from app.models.models import RoutineElement
from app.schemas.routine import RoutineItemBase, RoutineItemUpdate


class RoutineElementDAO(ProtectedBaseDAO):
    def get_routine_element_by_id(self, routine_element_id: int):
        routine_element = (
            self.db.query(RoutineElement)
            .filter(
                RoutineElement.id == routine_element_id,
                RoutineElement.user_id == self.user_id,
            )
            .first()
        )

        if not routine_element:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=DATA_DOES_NOT_EXIST,
            )

        return routine_element

    def get_routine_elements_by_routine_id(
        self, routine_id: int
    ) -> list[RoutineElement]:
        routine_elements = (
            self.db.query(RoutineElement)
            .filter(
                RoutineElement.routine_id == routine_id,
                RoutineElement.user_id == self.user_id,
            )
            .order_by(asc(RoutineElement.order))
            .all()
        )

        return routine_elements

    def update_routine_element(
        self,
        routine_element: RoutineElement,
        title: str | None,
        order: int | None,
        duration_minutes: int | None,
    ):
        routine_element.title = title or routine_element.title
        routine_element.order = order or routine_element.order
        routine_element.duration_minutes = (
            duration_minutes or routine_element.duration_minutes
        )

        return routine_element

    def update_routine_element_by_id(
        self,
        routine_element_id: int,
        title: str | None,
        order: int | None,
        duration_minutes: int | None,
    ):
        routine_element = self.get_routine_element_by_id(routine_element_id)
        routine_element_result = self.update_routine_element(
            routine_element=routine_element,
            title=title,
            order=order,
            duration_minutes=duration_minutes,
        )

        return routine_element_result

    def delete_routine_element(self, routine_element: RoutineElement) -> None:
        self.db.delete(routine_element)

    def delete_routine_element_by_id(self, routine_element_id: int) -> None:
        routine_element = self.get_routine_element_by_id(routine_element_id)
        self.delete_routine_element(routine_element)

    def create_routine_element(
        self,
        routine_id: int,
        title: str,
        order: int,
        duration_minutes: int,
    ) -> RoutineElement:
        routine_element = RoutineElement(
            user_id=self.user_id,
            routine_id=routine_id,
            title=title,
            order=order,
            duration_minutes=duration_minutes,
        )

        self.db.add(routine_element)

        return routine_element

    def update_routine_elements(
        self,
        routine_id: int,
        routine_elements: list[RoutineElement],
        updates_routine_elements: list[RoutineItemUpdate],
    ) -> list[RoutineElement]:
        routine_elements_dict = {
            routine_element.id: routine_element
            for routine_element in routine_elements
        }

        for index, update_routine_element in enumerate(
            updates_routine_elements
        ):
            routine_element = routine_elements_dict.get(
                update_routine_element.id
            )

            if routine_element and routine_id == routine_element.routine_id:
                self.update_routine_element(
                    routine_element=routine_element,
                    title=update_routine_element.title,
                    order=index,
                    duration_minutes=update_routine_element.duration_minutes,
                )

                routine_elements_dict.pop(update_routine_element.id)
            elif update_routine_element.id is None:
                self.create_routine_element(
                    routine_id=routine_id,
                    title=update_routine_element.title,
                    order=index,
                    duration_minutes=update_routine_element.duration_minutes,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=DATA_DOES_NOT_EXIST,
                )

        for routine_element in routine_elements_dict.values():
            self.delete_routine_element(routine_element)

        return self.get_routine_elements_by_routine_id(routine_id)

    def create_routine_elements(
        self,
        routine_id: int,
        routine_elements: list[RoutineItemBase],
    ) -> list[RoutineElement]:
        elements = [
            RoutineElement(
                user_id=self.user_id,
                title=item.title,
                order=index,
                duration_minutes=item.duration_minutes,
                routine_id=routine_id,
            )
            for index, item in enumerate(routine_elements)
        ]

        self.db.add_all(elements)

        return elements
