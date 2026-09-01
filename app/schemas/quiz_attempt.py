from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.quiz import QuizResponse
from app.schemas.user_answer import UserAnswerResponse


class QuizAttemptCreate(BaseModel):
    total_score: float
    is_completed: bool = False
    total_questions: int
    correct_count: int
    time_start: datetime | None = None
    time_submitted: datetime | None = None
    user_id: int
    quiz_id: int

# class QuizAttemptUpdate(BaseModel):
#     total_score: float | None = None
#     is_completed: bool | None = None
#     total_questions: int | None = None
#     correct_count: int | None = None
#     time_start: datetime | None = None
#     time_submitted: datetime | None = None

class QuizAttemptResponse(BaseModel):
    id: int
    total_score: float
    is_completed: bool
    total_questions: int
    correct_count: int
    time_start: datetime | None = None
    time_submitted: datetime | None = None
    created_date: datetime
    user_id: int
    quiz: QuizResponse

    model_config = ConfigDict(from_attributes=True)

class QuizAttemptDetailResponse(QuizAttemptResponse):
    user_answers: list[UserAnswerResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class StudentAnswer(BaseModel):
    question_id: int
    selected_option_id: int

class QuizSubmitRequest(BaseModel):
    answers: list[StudentAnswer]
    time_start: datetime | None = None
