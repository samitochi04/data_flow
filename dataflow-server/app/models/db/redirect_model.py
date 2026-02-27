from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Redirect(Base):
    """
    Redirect model for managing URL redirects when posts are moved or deleted.
    """
    __tablename__ = "redirects"

    id: Mapped[int] = mapped_column(primary_key=True)
    old_slug: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, index=True)
    new_slug: Mapped[str] = mapped_column(String(500), nullable=False)
    redirect_type: Mapped[str] = mapped_column(String(10), nullable=False, default="301")  # 301, 302, 307
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Redirect(id={self.id}, old_slug={self.old_slug}, new_slug={self.new_slug})>"
