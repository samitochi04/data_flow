from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.blog_post_model import BlogPost
from app.models.schemas.blog_post_schema import BlogPostCreate, BlogPostUpdate


class BlogPostRepository:
    """Repository for BlogPost database operations"""

    @staticmethod
    async def create(data: dict, db: AsyncSession) -> BlogPost:
        """Create a new blog post"""
        post = BlogPost(**data)
        db.add(post)
        await db.commit()
        await db.refresh(post)
        return post

    @staticmethod
    async def get_by_id(post_id: int, db: AsyncSession) -> Optional[BlogPost]:
        """Get post by ID"""
        stmt = select(BlogPost).where(BlogPost.id == post_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_slug(slug: str, db: AsyncSession) -> Optional[BlogPost]:
        """Get post by slug"""
        stmt = select(BlogPost).where(BlogPost.slug == slug)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_published(skip: int = 0, limit: int = 10, db: AsyncSession = None) -> List[BlogPost]:
        """Get all published posts with pagination"""
        stmt = (
            select(BlogPost)
            .where(BlogPost.status == "published")
            .order_by(desc(BlogPost.published_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_drafts(author_id: int, db: AsyncSession) -> List[BlogPost]:
        """Get all draft posts for an author"""
        stmt = select(BlogPost).where(
            and_(BlogPost.status == "draft", BlogPost.author_id == author_id)
        ).order_by(desc(BlogPost.created_at))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_category(category_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = None) -> List[BlogPost]:
        """Get posts by category with pagination"""
        stmt = (
            select(BlogPost)
            .where(and_(BlogPost.category_id == category_id, BlogPost.status == "published"))
            .order_by(desc(BlogPost.published_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update(post: BlogPost, data: dict, db: AsyncSession) -> BlogPost:
        """Update a blog post"""
        for key, value in data.items():
            if value is not None:
                setattr(post, key, value)
        await db.commit()
        await db.refresh(post)
        return post

    @staticmethod
    async def delete(post: BlogPost, db: AsyncSession) -> None:
        """Delete a blog post"""
        db.delete(post)
        await db.commit()

    @staticmethod
    async def slug_exists(slug: str, db: AsyncSession, exclude_id: Optional[int] = None) -> bool:
        """Check if slug already exists"""
        stmt = select(BlogPost).where(BlogPost.slug == slug)
        if exclude_id:
            stmt = stmt.where(BlogPost.id != exclude_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None
