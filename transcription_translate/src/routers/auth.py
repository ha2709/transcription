# src/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_db
from src.repositories.user import UserRepository
from src.schemas.user import Token, UserCreate, UserLogin, UserRead
from src.services.user import UserService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: AsyncSession = Depends(get_async_db)):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    try:
        user = await user_service.register_user(user_create)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_async_db)):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    try:
        token = await user_service.login_user(user_login)
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
