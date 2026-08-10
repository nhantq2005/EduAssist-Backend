from datetime import datetime
from sqlalchemy import String, DateTime, Double, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    explaination: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float] = mapped_column(Double, nullable=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False)

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")

    options: Mapped[list["Option"]] = relationship(back_populates="question")
    user_answers: Mapped[list["UserAnswer"]] = relationship(back_populates="question")

