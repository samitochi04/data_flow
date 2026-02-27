from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, func, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BlogPost(Base):
    """
    BlogPost model - the core content entity.
    Comprehensive blog post with SEO, social sharing, analytics, and content management.
    Relations: Many-to-One with User (author), Category, TopicCluster, Media (featured_image, og_image)
              One-to-Many with Comments, PostTags, PostViews, PostAnalytics
    """
    __tablename__ = "blog_posts"

    # Primary & Foreign Keys
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    topic_cluster_id: Mapped[Optional[int]] = mapped_column(ForeignKey("topic_clusters.id", ondelete="SET NULL"), nullable=True)
    featured_image_id: Mapped[Optional[int]] = mapped_column(ForeignKey("media.id", ondelete="SET NULL"), nullable=True)
    og_image_id: Mapped[Optional[int]] = mapped_column(ForeignKey("media.id", ondelete="SET NULL"), nullable=True)

    # Core Content
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Status & Publishing
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")  # draft, published, archived, scheduled
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # SEO Metadata
    meta_description: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    meta_keywords: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    canonical_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Social Sharing
    og_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    og_description: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    twitter_card_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # summary, summary_large_image

    # Analytics & Stats (denormalized for performance)
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    like_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    share_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    author: Mapped["User"] = relationship("User", foreign_keys=[author_id], backref="blog_posts")
    category: Mapped[Optional["Category"]] = relationship("Category", foreign_keys=[category_id], back_populates="posts")
    topic_cluster: Mapped[Optional["TopicCluster"]] = relationship("TopicCluster", foreign_keys=[topic_cluster_id], back_populates="posts")
    featured_image: Mapped[Optional["Media"]] = relationship("Media", foreign_keys=[featured_image_id])
    og_image: Mapped[Optional["Media"]] = relationship("Media", foreign_keys=[og_image_id])

    # One-to-Many relationships (uncommented after models exist)
    # comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    # post_tags: Mapped[List["PostTag"]] = relationship("PostTag", back_populates="post", cascade="all, delete-orphan")
    # post_views: Mapped[List["PostView"]] = relationship("PostView", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<BlogPost(id={self.id}, title={self.title}, slug={self.slug}, status={self.status})>"
