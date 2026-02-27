from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, func, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Comment(Base):
    """
    Comment model for blog post comments.
    Supports nested replies through parent_id (self-referential).
    Uses fingerprinting for anonymous user tracking.
    """
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("blog_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True
    )

    # Commenter Info (anonymous)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    fingerprint_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Content & Moderation
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    like_count: Mapped[int] = mapped_column(nullable=False, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    post: Mapped["BlogPost"] = relationship("BlogPost", foreign_keys=[post_id], backref="comments")
    parent: Mapped[Optional["Comment"]] = relationship(
        "Comment",
        remote_side=[id],
        backref="replies",
        foreign_keys=[parent_id]
    )

    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, post_id={self.post_id}, name={self.name})>"
