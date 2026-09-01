from pydantic import BaseModel, ConfigDict
from app.schemas.option import OptionResponse
from app.schemas.question import QuestionResponse


class UserAnswerCreate(BaseModel):
    is_correct: bool
    question_id: int
    option_id: int
    quiz_attempt_id: int

class UserAnswerUpdate(BaseModel):
    is_correct: bool | None = None
    question_id: int | None = None
    option_id: int | None = None
    quiz_attempt_id: int | None = None

class UserAnswerResponse(BaseModel):
    id: int
    is_correct: bool
    question_id: int
    option_id: int
    quiz_attempt_id: int
    question: QuestionResponse | None = None
    option: OptionResponse | None = None

    model_config = ConfigDict(from_attributes=True)
