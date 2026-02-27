from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.user_model import User


class UserRepository:
    """Repository for user database operations"""

    @staticmethod
    async def create(data: dict, db: AsyncSession) -> User:
        """Create a new user"""
        user = User(**data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_by_email(email: str, db: AsyncSession) -> User | None:
        """Get user by email"""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(user_id: int, db: AsyncSession) -> User | None:
        """Get user by id"""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_active(db: AsyncSession) -> list[User]:
        """Get all active users"""
        stmt = select(User).where(User.is_active == True)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update(user: User, data: dict, db: AsyncSession) -> User:
        """Update user"""
        for key, value in data.items():
            if value is not None:
                setattr(user, key, value)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete(user: User, db: AsyncSession) -> None:
        """Delete user"""
        db.delete(user)
        await db.commit()
