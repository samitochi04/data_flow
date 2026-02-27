from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.schemas.blog_post_schema import BlogPostCreate, BlogPostUpdate, BlogPostOut
from app.repositories.blog_post_repository import BlogPostRepository


class BlogPostService:
    """Service layer for blog post business logic"""

    @staticmethod
    async def create_post(data: BlogPostCreate, author_id: int, db: AsyncSession) -> BlogPostOut:
        """Create new blog post (admin only) - starts as draft"""
        # Check for slug uniqueness
        if await BlogPostRepository.slug_exists(data.slug, db):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Post slug already exists"
            )
        
        post_data = data.model_dump()
        post_data['author_id'] = author_id
        post_data['status'] = 'draft'
        
        post = await BlogPostRepository.create(post_data, db)
        return BlogPostOut.model_validate(post)

    @staticmethod
    async def get_post(post_id: int, db: AsyncSession) -> BlogPostOut:
        """Get post by ID"""
        post = await BlogPostRepository.get_by_id(post_id, db)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        return BlogPostOut.model_validate(post)

    @staticmethod
    async def get_post_by_slug(slug: str, db: AsyncSession) -> BlogPostOut:
        """Get published post by slug"""
        post = await BlogPostRepository.get_by_slug(slug, db)
        if not post or post.status != "published":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        return BlogPostOut.model_validate(post)

    @staticmethod
    async def list_published(skip: int = 0, limit: int = 10, db: AsyncSession = None):
        """List all published posts"""
        posts = await BlogPostRepository.get_published(skip, limit, db)
        return [BlogPostOut.model_validate(p) for p in posts]

    @staticmethod
    async def list_drafts(author_id: int, db: AsyncSession):
        """List all draft posts for an author"""
        posts = await BlogPostRepository.get_drafts(author_id, db)
        return [BlogPostOut.model_validate(p) for p in posts]

    @staticmethod
    async def update_post(post_id: int, data: BlogPostUpdate, author_id: int, db: AsyncSession) -> BlogPostOut:
        """Update post (only by author or admin)"""
        post = await BlogPostRepository.get_by_id(post_id, db)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        
        if post.author_id != author_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this post")
        
        # Check slug uniqueness if changing
        if data.slug and data.slug != post.slug:
            if await BlogPostRepository.slug_exists(data.slug, db, exclude_id=post_id):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already exists")
        
        update_data = data.model_dump(exclude_unset=True)
        post = await BlogPostRepository.update(post, update_data, db)
        return BlogPostOut.model_validate(post)

    @staticmethod
    async def publish_post(post_id: int, author_id: int, db: AsyncSession) -> BlogPostOut:
        """Publish a draft post"""
        post = await BlogPostRepository.get_by_id(post_id, db)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        
        if post.author_id != author_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        
        if post.status != "draft":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft posts can be published")
        
        update_data = {
            "status": "published",
            "published_at": datetime.utcnow()
        }
        post = await BlogPostRepository.update(post, update_data, db)
        return BlogPostOut.model_validate(post)

    @staticmethod
    async def delete_post(post_id: int, author_id: int, db: AsyncSession) -> None:
        """Archive a post (soft delete)"""
        post = await BlogPostRepository.get_by_id(post_id, db)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        
        if post.author_id != author_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        
        await BlogPostRepository.delete(post, db)
