from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from .question import QuestionRequest
from .subject import SubjectResponse
from app.models.quiz import DifficultyLevel, SourceType

class QuizCreate(BaseModel):
    title: str
    description: str
    source_type: SourceType
    difficulty_level: DifficultyLevel
    subject_id: Optional[int]
    is_public: bool = True

class QuizData(BaseModel):
    questions: List[QuestionRequest]

class QuizGenerateRequest(BaseModel):
    topic: str
    num_questions: int = 5
    subject_id: int
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    is_public: bool = False

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    source_type: Optional[SourceType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    subject_id: Optional[int] = None
    is_public: Optional[bool] = None

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