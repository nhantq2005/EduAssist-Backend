from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Flashcard(Base):
    __tablename__ = "flashcards"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    front: Mapped[str] = mapped_column(String, nullable=False)
    back: Mapped[str] = mapped_column(String, nullable=False)
    flashcard_set_id: Mapped[int] = mapped_column(ForeignKey("flashcard_sets.id"), nullable=False)

    flashcard_set: Mapped["FlashcardSet"] = relationship(back_populates="flashcards")