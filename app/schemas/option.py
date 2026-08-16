from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class OptionRequest(BaseModel):
    id: Optional[int] = Field(default=None)
    content: str
    is_correct: bool
    question_id: Optional[int] = Field(default=None)

class OptionResponse(BaseModel):
    id: int
    content: str
    is_correct: bool
    question_id: int

    model_config = ConfigDict(from_attributes=True)