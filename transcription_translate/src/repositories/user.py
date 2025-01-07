# src/repositories/user_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.user import User
from src.schemas.user import UserCreate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def get_by_username(self, username: str) -> User:
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    async def create_user(self, user_create: UserCreate, hashed_password: str) -> User:
        new_user = User(
            email=user_create.email,
            username=user_create.username,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            hashed_password=hashed_password,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
