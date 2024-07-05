from uuid import UUID, uuid4
from sqlmodel import SQLModel as _SQLModel, Field, select
from sqlalchemy.orm import declared_attr
from datetime import datetime, timezone
from typing import Type, TypeVar, List
from sqlalchemy.ext.asyncio import AsyncSession

class SQLModel(_SQLModel):
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__

VSQLModelType = TypeVar("VSQLModelType", bound="VSQLModel")


class VSQLModel(SQLModel):
    
    """
    Deriving this class will validate all fields upon instantiation and during
    update.
    """

    model_config = {
        "validate_assignment": True,
        "protected_namespaces": (),
    }

    """
    Default Fields:
        id: uuid of the model
        created_at: when the model was created
        updated_at: when the model was last updated
    """

    id: UUID = Field(
        default_factory=uuid4, primary_key=True, nullable=False, index=True
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": datetime.now(timezone.utc)}
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"}
    )
    @classmethod
    async def get_all(cls: Type[VSQLModelType], session: AsyncSession) -> List[VSQLModelType]:
        """
        Get all the model items.

        Args:
            session (AsyncSession): An async session.

        Returns:
            List[VSQLModelType]: A list of model items.
        """
        data = await session.execute(select(cls))
        data = data.scalars().all()
        return data


    @classmethod
    async def delete_all(cls: Type[VSQLModelType], session: AsyncSession) -> List[VSQLModelType]:

        """
        Delete all the model items.

        Args:
            session (AsyncSession): An async session.

        Returns:
            List[VSQLModelType]: A list of model items that are deleted.
        """
        data = await session.get(cls)
        await session.delete(data)
        return data
        ...

    @classmethod
    async def get_by_id(cls: Type[VSQLModelType], id: UUID, session: AsyncSession) -> VSQLModelType:
        """
        Get a model item by ID.

        Args:
            id (UUID): ID.
            session (AsyncSession): An async session.

        Returns:
            VSQLModelType: A model item.
        """
        data = await session.execute(select(cls).where(cls.id == id))
        data = data.scalar_one_or_none()
        return data

    @classmethod
    async def delete_by_id(cls: Type[VSQLModelType], id: UUID, session: AsyncSession) -> VSQLModelType:
        """
        Delete a model item by ID.

        Args:
            id (UUID): ID.
            session (AsyncSession): An async session.

        Returns:
            VSQLModelType: A model item that is deleted.
        """
        data = await session.get(cls, id)
        await session.delete(data)
        return data