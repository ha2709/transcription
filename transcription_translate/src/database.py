import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from src.models.task import Task
from src.models.user import User

load_dotenv()
# DATABASE_URL = "postgresql://admin:1234@localhost/pinchi"
DATABASE_URL = os.environ.get("DATABASE_URL")
print(12, DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=False, poolclass=NullPool)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
