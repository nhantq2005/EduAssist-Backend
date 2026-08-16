from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional
from app.schemas.option import OptionResponse, OptionRequest


class QuestionRequest(BaseModel):
    question: str
    # score: float = Field(default=1.0, description="Điểm của câu hỏi")
    quiz_id: Optional[int] = Field(default=None)
    explanation: Optional[str] = Field(default=None)
    options: List[OptionRequest]

class QuestionResponse(BaseModel):
    id: int
    question: str
    explanation: Optional[str] = None
    score : Optional[float] = None
    created_date: datetime
    quiz_id: Optional[int] = None
    options: List[OptionResponse]

    model_config = ConfigDict(from_attributes=True)