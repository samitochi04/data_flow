from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Category(Base):
    """
    Category model for organizing blog posts into nested categories.
    Supports hierarchical structure via parent_id (self-referential).
    """
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Self-referential relationships for nested categories
    parent: Mapped[Optional["Category"]] = relationship(
        "Category",
        remote_side=[id],
        backref="children",
        foreign_keys=[parent_id]
    )

    # One-to-Many with blog_posts (forward reference - BlogPost model not yet created)
    # Will be uncommented after BlogPost model exists

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name}, slug={self.slug})>"
