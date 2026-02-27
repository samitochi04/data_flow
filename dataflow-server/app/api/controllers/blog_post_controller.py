from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.blog_post_schema import BlogPostCreate, BlogPostUpdate, BlogPostOut
from app.services.blog_post_service import BlogPostService


class BlogPostController:
    """Controller for blog post HTTP operations"""

    @staticmethod
    async def create(data: BlogPostCreate, author_id: int, db: AsyncSession) -> BlogPostOut:
        """Create new blog post"""
        return await BlogPostService.create_post(data, author_id, db)

    @staticmethod
    async def get(post_id: int, db: AsyncSession) -> BlogPostOut:
        """Get post by ID"""
        return await BlogPostService.get_post(post_id, db)

    @staticmethod
    async def get_by_slug(slug: str, db: AsyncSession) -> BlogPostOut:
        """Get post by slug"""
        return await BlogPostService.get_post_by_slug(slug, db)

    @staticmethod
    async def list_published(skip: int = 0, limit: int = 10, db: AsyncSession = None):
        """List published posts"""
        return await BlogPostService.list_published(skip, limit, db)

    @staticmethod
    async def list_drafts(author_id: int, db: AsyncSession):
        """List draft posts"""
        return await BlogPostService.list_drafts(author_id, db)

    @staticmethod
    async def update(post_id: int, data: BlogPostUpdate, author_id: int, db: AsyncSession) -> BlogPostOut:
        """Update post"""
        return await BlogPostService.update_post(post_id, data, author_id, db)

    @staticmethod
    async def publish(post_id: int, author_id: int, db: AsyncSession) -> BlogPostOut:
        """Publish post"""
        return await BlogPostService.publish_post(post_id, author_id, db)

    @staticmethod
    async def delete(post_id: int, author_id: int, db: AsyncSession) -> None:
        """Delete post"""
        return await BlogPostService.delete_post(post_id, author_id, db)
