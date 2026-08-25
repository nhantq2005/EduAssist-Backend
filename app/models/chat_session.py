from datetime import datetime

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    created_date: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_date: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="chat_sessions")

    chat_messages: Mapped[list["ChatMessage"]] = relationship(back_populates="chat_session", cascade="all, delete-orphan")

    def __str__(self) -> str:
        return f"{self.title}"