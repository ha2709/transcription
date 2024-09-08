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
# engine = create_engine(DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)
AsyncSessionFactory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# Dependency to get the database session
async def get_async_db():
    async with AsyncSessionFactory() as session:
        yield session


# Import all modules here that might define models so that
# they are registered properly on the metadata. Otherwise,
# SQLAlchemy might not be aware of them.


# from models.verfication_token import VerificationToken


# async def create_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


# If there's an existing event loop, use it to run the coroutine
# loop = asyncio.get_event_loop()
# if loop.is_running():
#     loop.create_task(create_tables())
# else:
#     asyncio.run(create_tables())
