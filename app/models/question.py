from datetime import datetime

from sqlalchemy import DateTime, Double, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    explanation: Mapped[str | None] = mapped_column(String, nullable=True)
    score: Mapped[float | None] = mapped_column(Double, nullable=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False)

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")

    options: Mapped[list["Option"]] = relationship(back_populates="question", cascade="all, delete-orphan")
    user_answers: Mapped[list["UserAnswer"]] = relationship(back_populates="question", cascade="all, delete-orphan")

    def __str__(self) -> str:
        return self.question
