from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, func, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PostAnalytic(Base):
    """
    PostAnalytic model - One-to-One with BlogPost.
    Aggregated analytics calculated from PostView records.
    """
    __tablename__ = "post_analytics"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("blog_posts.id", ondelete="CASCADE"),
        primary_key=True
    )
    avg_time: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # Average time spent (seconds)
    bounce_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # 0-100
    total_views: Mapped[int] = mapped_column(nullable=False, default=0)
    last_calculated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationship
    post: Mapped["BlogPost"] = relationship("BlogPost", foreign_keys=[post_id], backref="analytics")

    def __repr__(self) -> str:
        return f"<PostAnalytic(post_id={self.post_id}, avg_time={self.avg_time}, bounce_rate={self.bounce_rate})>"
