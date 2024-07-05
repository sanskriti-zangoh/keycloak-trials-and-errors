from database.models.base import VSQLModel, VSQLModelType
from sqlmodel import Field, Column, select, Relationship
from datetime import datetime
from typing import Optional, Type, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import String
from pydantic  import EmailStr, HttpUrl

UsersType = TypeVar("UsersType", bound="Users")



class Users(VSQLModel, table=True):

    """
    Users model for the registered users.

    Fields:
        id: ID of the user.
        name: Name of the user.
        username: Username of the user.
        email: Email of the user.
        active: If True, the user is active.
        created_at: Created at.
        updated_at: Last Updated at.
    """
    name: str = Field(index=True, nullable=False)
    username: str = Field(index=True, nullable=False, unique=True)
    email: EmailStr = Field(sa_column=Column(String, index=True, unique=True))
    pic: Optional[HttpUrl] = Field(sa_column=Column(String, nullable=True))
    active: bool = Field(default=False)

    @classmethod
    async def get_by_username(cls: Type[UsersType], username: str, session: AsyncSession) -> UsersType:
        """
        Get a user by username.

        Args:
            username (str): Username of the user.
            session (AsyncSession): An async session.

        Returns:
            UsersType: A user.
        """
        data = await session.execute(select(cls).where(cls.username == username))
        data = data.scalar_one_or_none()
        return data
    
    @classmethod
    async def get_by_email(cls: Type[UsersType], email: EmailStr, session: AsyncSession) -> UsersType:
        """
        Get a user by email.

        Args:
            email (EmailStr): Email of the user.
            session (AsyncSession): An async session.

        Returns:
            UsersType: A user.
        """
        data = await session.execute(select(cls).where(cls.email == email))
        data = data.scalar_one_or_none()
        return data