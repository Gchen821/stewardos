from typing import Any, Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class SQLAlchemyRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: Session):
        self.session = session

    def get(self, entity_id: Any) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def list(self, *conditions: Any, order_by: Any | None = None) -> list[ModelT]:
        stmt: Select[tuple[ModelT]] = select(self.model)
        for condition in conditions:
            stmt = stmt.where(condition)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        return list(self.session.scalars(stmt).all())

    def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        self.session.flush()
        self.session.refresh(instance)
        return instance

    def delete(self, instance: ModelT) -> None:
        self.session.delete(instance)
        self.session.flush()
