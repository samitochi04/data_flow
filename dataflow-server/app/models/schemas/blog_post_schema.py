from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BlogPostBase(BaseModel):
    """Base fields for blog posts"""
    title: str = Field(..., min_length=1, max_length=500)
    slug: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=10)
    excerpt: Optional[str] = Field(None, max_length=1000)
    category_id: Optional[int] = None
    topic_cluster_id: Optional[int] = None
    featured_image_id: Optional[int] = None
    og_image_id: Optional[int] = None


class BlogPostCreate(BlogPostBase):
    """Schema for creating blog post"""
    pass


class BlogPostUpdate(BaseModel):
    """Schema for updating blog post"""
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    category_id: Optional[int] = None
    topic_cluster_id: Optional[int] = None
    meta_description: Optional[str] = None


class BlogPostPublish(BaseModel):
    """Schema for publishing post"""
    publish: bool = True


class BlogPostOut(BlogPostBase):
    """Schema for blog post output"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    author_id: int
    status: str
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    view_count: int
    like_count: int
    comment_count: int
