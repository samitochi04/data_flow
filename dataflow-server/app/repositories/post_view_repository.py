from typing import Optional, List
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.post_view_model import PostView


class PostViewRepository:
    """Repository for PostView database operations"""

    @staticmethod
    async def create(data: dict, db: AsyncSession) -> PostView:
        """Create post view record"""
        view = PostView(**data)
        db.add(view)
        await db.commit()
        await db.refresh(view)
        return view

    @staticmethod
    async def get_by_id(view_id: int, db: AsyncSession) -> Optional[PostView]:
        """Get post view by ID"""
        stmt = select(PostView).where(PostView.id == view_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_post_views(post_id: int, skip: int = 0, limit: int = 100, db: AsyncSession = None) -> List[PostView]:
        """Get views for a specific post"""
        stmt = (
            select(PostView)
            .where(PostView.post_id == post_id)
            .order_by(desc(PostView.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def user_viewed_post(post_id: int, fingerprint_hash: str, db: AsyncSession) -> Optional[PostView]:
        """Get existing view from same user for a post"""
        stmt = select(PostView).where(
            and_(PostView.post_id == post_id, PostView.fingerprint_hash == fingerprint_hash)
        ).order_by(desc(PostView.created_at)).limit(1)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
