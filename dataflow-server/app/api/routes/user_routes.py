from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.controllers.user_controller import UserController
from app.core.database import get_db
from app.models.schemas.user_schema import UserCreate, UserOut, UserLogin

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new admin user.
    Only admins can create other admin users.
    """
    return await UserController.create_user(payload, db)


@router.post("/login")
async def login_user(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    """
    return await UserController.authenticate_user(payload, db)
