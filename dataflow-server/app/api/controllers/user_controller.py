from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.user_schema import UserCreate, UserLogin
from app.services.user_service import UserService


class UserController:
    """User controller - handles user-related HTTP operations"""

    @staticmethod
    async def create_user(data: UserCreate, db: AsyncSession):
        """Create a new user (admin registration)"""
        user = await UserService.create_user(data, db)
        return user

    @staticmethod
    async def authenticate_user(data: UserLogin, db: AsyncSession):
        """Authenticate user and return token"""
        token = await UserService.authenticate_user(data.email, data.password, db)
        return token
