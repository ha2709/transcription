import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional

# Load environment variables from .env
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.models.user import User
from src.repositories.user import UserRepository
from src.schemas.user import Token, UserCreate, UserLogin

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def register_user(self, user_create: UserCreate) -> User:
        existing_user = await self.user_repository.get_by_email(user_create.email)
        if existing_user:
            raise ValueError("Email already registered")

        existing_username = await self.user_repository.get_by_username(
            user_create.username
        )
        if existing_username:
            raise ValueError("Username already taken")

        hashed_password = self.get_password_hash(user_create.password)
        new_user = await self.user_repository.create_user(user_create, hashed_password)
        return new_user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def login_user(self, user_login: UserLogin) -> Token:
        user = await self.authenticate_user(user_login.email, user_login.password)
        if not user:
            raise ValueError("Invalid email or password")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
