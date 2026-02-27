from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas.blog_post_schema import BlogPostCreate, BlogPostUpdate, BlogPostOut
from app.api.controllers.blog_post_controller import BlogPostController

router = APIRouter(prefix="/posts", tags=["Blog Posts"])


@router.post("", response_model=BlogPostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: BlogPostCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new blog post (draft status)"""
    # TODO: Get author_id from JWT token middleware
    author_id = 1  # Placeholder - will come from auth
    return await BlogPostController.create(payload, author_id, db)


@router.get("", response_model=list[BlogPostOut])
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all published posts with pagination"""
    return await BlogPostController.list_published(skip, limit, db)


@router.get("/admin/drafts", response_model=list[BlogPostOut])
async def list_drafts(
    db: AsyncSession = Depends(get_db)
):
    """List all draft posts (admin only)"""
    # TODO: Get author_id from JWT token
    author_id = 1
    return await BlogPostController.list_drafts(author_id, db)


@router.get("/{post_id}", response_model=BlogPostOut)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get post by ID"""
    return await BlogPostController.get(post_id, db)


@router.get("/slug/{slug}", response_model=BlogPostOut)
async def get_post_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get published post by slug"""
    return await BlogPostController.get_by_slug(slug, db)


@router.put("/{post_id}", response_model=BlogPostOut)
async def update_post(
    post_id: int,
    payload: BlogPostUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update post"""
    # TODO: Get author_id from JWT
    author_id = 1
    return await BlogPostController.update(post_id, payload, author_id, db)


@router.patch("/{post_id}/publish", response_model=BlogPostOut)
async def publish_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Publish a draft post"""
    # TODO: Get author_id from JWT
    author_id = 1
    return await BlogPostController.publish(post_id, author_id, db)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete/archive post"""
    # TODO: Get author_id from JWT
    author_id = 1
    await BlogPostController.delete(post_id, author_id, db)
