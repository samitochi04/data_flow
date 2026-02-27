from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.comment_model import Comment


class CommentRepository:
    """Repository for Comment database operations"""

    @staticmethod
    async def create(data: dict, db: AsyncSession) -> Comment:
        """Create a new comment"""
        comment = Comment(**data)
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment

    @staticmethod
    async def get_by_id(comment_id: int, db: AsyncSession) -> Optional[Comment]:
        """Get comment by ID"""
        stmt = select(Comment).where(Comment.id == comment_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_post(post_id: int, skip: int = 0, limit: int = 20, db: AsyncSession = None) -> List[Comment]:
        """Get approved comments for a post"""
        stmt = (
            select(Comment)
            .where(and_(Comment.post_id == post_id, Comment.is_approved == True, Comment.parent_id == None))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_unapproved(db: AsyncSession) -> List[Comment]:
        """Get all unapproved comments (admin only)"""
        stmt = select(Comment).where(Comment.is_approved == False)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update(comment: Comment, data: dict, db: AsyncSession) -> Comment:
        """Update comment"""
        for key, value in data.items():
            if value is not None:
                setattr(comment, key, value)
        await db.commit()
        await db.refresh(comment)
        return comment

    @staticmethod
    async def delete(comment: Comment, db: AsyncSession) -> None:
        """Delete comment"""
        db.delete(comment)
        await db.commit()
