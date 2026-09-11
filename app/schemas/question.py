from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.option import OptionRequest, OptionResponse


class QuestionRequest(BaseModel):
    question: str
    # score: float = Field(default=1.0)
    quiz_id: int | None = Field(default=None)
    explanation: str | None = Field(default=None)
    options: list[OptionRequest]

class QuestionResponse(BaseModel):
    id: int
    question: str
    explanation: str | None = None
    score : float | None = None
    created_date: datetime
    quiz_id: int | None = None
    options: list[OptionResponse]

    model_config = ConfigDict(from_attributes=True)