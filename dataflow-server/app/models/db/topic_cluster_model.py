from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TopicCluster(Base):
    """
    TopicCluster model for organizing blog posts into topic clusters.
    Represents a pillar content hub with related blog posts grouped together.
    pillar_post: The main guide/pillar post for this topic cluster (forward reference to BlogPost)
    """
    __tablename__ = "topic_clusters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    pillar_post_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("blog_posts.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # One-to-Many with blog_posts
    posts: Mapped[list["BlogPost"]] = relationship(
        "BlogPost",
        foreign_keys="BlogPost.topic_cluster_id",
        back_populates="topic_cluster"
    )

    def __repr__(self) -> str:
        return f"<TopicCluster(id={self.id}, name={self.name}, slug={self.slug})>"
