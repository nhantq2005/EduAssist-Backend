from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.quiz import DifficultyLevel, SourceType
from .question import QuestionRequest


class QuizCreate(BaseModel):
    title: str
    description: str
    source_type: SourceType
    difficulty_level: DifficultyLevel
    subject_id: int | None
    is_public: bool = True

class QuizData(BaseModel):
    questions: list[QuestionRequest]

class QuizGenerateRequest(BaseModel):
    topic: str
    num_questions: int = 5
    subject_id: int
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    is_public: bool = False

class QuizUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    source_type: SourceType | None = None
    difficulty_level: DifficultyLevel | None = None
    subject_id: int | None = None
    is_public: bool | None = None

class QuizResponse(BaseModel):
    id: int
    title: str
    description: str
    source_type: SourceType
    difficulty_level: DifficultyLevel
    created_date: datetime
    updated_date: datetime
    subject_id: int
    created_by: int
    is_public: bool

    model_config = ConfigDict(from_attributes=True)