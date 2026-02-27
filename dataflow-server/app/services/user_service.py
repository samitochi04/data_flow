from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.schemas.user_schema import UserCreate
from app.repositories.user_repository import UserRepository
from app.utils.password_utils import hash_password, verify_password


class UserService:
    """Service for user business logic"""

    @staticmethod
    async def create_user(data: UserCreate, db: AsyncSession):
        """
        Create a new user.
        Checks if user already exists by email.
        """
        # Check if user already exists
        existing_user = await UserRepository.get_by_email(data.email, db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        # Hash password
        password_hash = hash_password(data.password)

        # Create user data dict
        user_data = {
            "name": data.name,
            "email": data.email,
            "password": password_hash,
            "role": "admin"
        }

        # Create user in database
        user = await UserRepository.create(user_data, db)
        return user

    @staticmethod
    async def authenticate_user(email: str, password: str, db: AsyncSession):
        """
        Authenticate user by email and password.
        Returns user if credentials are valid.
        """
        # Get user by email
        user = await UserRepository.get_by_email(email, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        return {"access_token": str(user.id), "token_type": "bearer"}
