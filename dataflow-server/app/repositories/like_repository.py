from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.like_model import Like


class LikeRepository:
    """Repository for Like database operations"""

    @staticmethod
    async def create(data: dict, db: AsyncSession) -> Like:
        """Create like"""
        like = Like(**data)
        db.add(like)
        await db.commit()
        await db.refresh(like)
        return like

    @staticmethod
    async def get_by_id(like_id: int, db: AsyncSession) -> Optional[Like]:
        """Get like by ID"""
        stmt = select(Like).where(Like.id == like_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def post_like_exists(post_id: int, fingerprint_hash: str, db: AsyncSession) -> bool:
        """Check if user already liked this post"""
        stmt = select(Like).where(
            and_(Like.post_id == post_id, Like.fingerprint_hash == fingerprint_hash)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def comment_like_exists(comment_id: int, fingerprint_hash: str, db: AsyncSession) -> bool:
        """Check if user already liked this comment"""
        stmt = select(Like).where(
            and_(Like.comment_id == comment_id, Like.fingerprint_hash == fingerprint_hash)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def delete_post_like(post_id: int, fingerprint_hash: str, db: AsyncSession) -> None:
        """Delete post like"""
        stmt = select(Like).where(
            and_(Like.post_id == post_id, Like.fingerprint_hash == fingerprint_hash)
        )
        result = await db.execute(stmt)
        like = result.scalar_one_or_none()
        if like:
            db.delete(like)
            await db.commit()

    @staticmethod
    async def delete_comment_like(comment_id: int, fingerprint_hash: str, db: AsyncSession) -> None:
        """Delete comment like"""
        stmt = select(Like).where(
            and_(Like.comment_id == comment_id, Like.fingerprint_hash == fingerprint_hash)
        )
        result = await db.execute(stmt)
        like = result.scalar_one_or_none()
        if like:
            db.delete(like)
            await db.commit()
