from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.media_model import Media


class MediaRepository:
    """Repository for Media database operations"""

    @staticmethod
    async def create(data: dict, db: AsyncSession) -> Media:
        """Create media record"""
        media = Media(**data)
        db.add(media)
        await db.commit()
        await db.refresh(media)
        return media

    @staticmethod
    async def get_by_id(media_id: int, db: AsyncSession) -> Optional[Media]:
        """Get media by ID"""
        stmt = select(Media).where(Media.id == media_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 20, db: AsyncSession = None) -> List[Media]:
        """Get all media with pagination"""
        stmt = select(Media).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete(media: Media, db: AsyncSession) -> None:
        """Delete media"""
        db.delete(media)
        await db.commit()
