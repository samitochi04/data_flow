from datetime import datetime

from sqlalchemy import DateTime, func, ForeignKey, String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PostView(Base):
    """
    PostView model - Many-to-One with BlogPost.
    Tracks individual page views with detailed analytics.
    Uses fingerprint_hash for anonymous user tracking.
    """
    __tablename__ = "post_views"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("blog_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    fingerprint_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    referrer_url: Mapped[str] = mapped_column(String(500), nullable=False, default="direct")
    user_agent: Mapped[str] = mapped_column(String(500), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, default="XX")
    device_type: Mapped[str] = mapped_column(String(50), nullable=False, default="desktop")  # mobile, tablet, desktop
    is_bounce: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        index=True  # Indexed for time-series queries
    )

    # Relationship
    post: Mapped["BlogPost"] = relationship("BlogPost", foreign_keys=[post_id], backref="post_views")

    def __repr__(self) -> str:
        return f"<PostView(id={self.id}, post_id={self.post_id}, device_type={self.device_type})>"
