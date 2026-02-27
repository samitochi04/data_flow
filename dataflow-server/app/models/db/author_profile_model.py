from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuthorProfile(Base):
    """
    AuthorProfile model for extended user information.
    One-to-One relationship with User model.
    Stores author-specific metadata like bio, social links, expertise.
    """
    __tablename__ = "author_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    bio: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    expertise_topics: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Comma-separated
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # One-to-One relationship with User
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        backref="author_profile"
    )

    def __repr__(self) -> str:
        return f"<AuthorProfile(id={self.id}, user_id={self.user_id})>"
