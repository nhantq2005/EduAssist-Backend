from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class FlashcardSet(Base):
    __tablename__ = "flashcard_sets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    document: Mapped["Document"] = relationship(back_populates="flashcard_sets")
    user: Mapped["User"] = relationship(back_populates="flashcard_sets")
    flashcards: Mapped[list["Flashcard"]] = relationship(back_populates="flashcard_set", cascade="all, delete-orphan")