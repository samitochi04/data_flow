from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, func, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Like(Base):
    """
    Like model for tracking likes on posts and comments.
    Can target either BlogPost or Comment (but not both - one must be null).
    Uses fingerprint_hash for anonymous user tracking.
    """
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("blog_posts.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    comment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    fingerprint_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    post: Mapped[Optional["BlogPost"]] = relationship("BlogPost", foreign_keys=[post_id], backref="likes")
    comment: Mapped[Optional["Comment"]] = relationship("Comment", foreign_keys=[comment_id], backref="likes")

    def __repr__(self) -> str:
        return f"<Like(id={self.id}, post_id={self.post_id}, comment_id={self.comment_id})>"
