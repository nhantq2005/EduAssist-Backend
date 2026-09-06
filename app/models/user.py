from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    LECTURER = "LECTURER"
    STUDENT = "STUDENT"

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    gender: Mapped[Gender] = mapped_column(SqlEnum(Gender), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    documents: Mapped[list["Document"]] = relationship(back_populates="lecturer")
    attempt_quizzes: Mapped[list["QuizAttempt"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    subjects: Mapped[list["Subject"]] = relationship(back_populates="lecturer")
    chat_sessions: Mapped[list["ChatSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    flashcard_sets: Mapped[list["FlashcardSet"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __str__(self):
        return self.name
