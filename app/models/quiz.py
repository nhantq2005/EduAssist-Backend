from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class SourceType(str, Enum):
    AI_GENERATED = "AI_GENERATED"
    TEACHER_CREATED = "TEACHER_CREATED"


class DifficultyLevel(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class Quiz(Base):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    source_type: Mapped[SourceType] = mapped_column(SqlEnum(SourceType), default=SourceType.TEACHER_CREATED)
    difficulty_level: Mapped[DifficultyLevel] = mapped_column(SqlEnum(DifficultyLevel))
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, default=1)
    is_public: Mapped[bool] = mapped_column(default=True)

    subject:Mapped["Subject"] = relationship(back_populates="quizzes")
    creator: Mapped["User"] = relationship()

    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(back_populates="quiz", cascade="all, delete-orphan")
    questions: Mapped[list["Question"]] = relationship(back_populates="quiz", cascade="all, delete-orphan")

    def __str__(self) -> str:
        return f"{self.title}"




