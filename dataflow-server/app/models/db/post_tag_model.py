from datetime import datetime

from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PostTag(Base):
    """
    PostTag model - Junction table for Many-to-Many relationship between BlogPost and Tag.
    """
    __tablename__ = "post_tags"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("blog_posts.id", ondelete="CASCADE"),
        primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    post: Mapped["BlogPost"] = relationship("BlogPost", foreign_keys=[post_id], backref="post_tags_relation")
    tag: Mapped["Tag"] = relationship("Tag", foreign_keys=[tag_id], backref="post_tags_relation")

    def __repr__(self) -> str:
        return f"<PostTag(post_id={self.post_id}, tag_id={self.tag_id})>"
