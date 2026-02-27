from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.tag_model import Tag


class TagRepository:
    """Repository for Tag database operations"""

    @staticmethod
    async def create(data: dict, db: AsyncSession) -> Tag:
        """Create tag"""
        tag = Tag(**data)
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
        return tag

    @staticmethod
    async def get_by_id(tag_id: int, db: AsyncSession) -> Optional[Tag]:
        """Get tag by ID"""
        stmt = select(Tag).where(Tag.id == tag_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_slug(slug: str, db: AsyncSession) -> Optional[Tag]:
        """Get tag by slug"""
        stmt = select(Tag).where(Tag.slug == slug)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Tag]:
        """Get all tags"""
        stmt = select(Tag)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete(tag: Tag, db: AsyncSession) -> None:
        """Delete tag"""
        db.delete(tag)
        await db.commit()
