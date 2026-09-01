from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentCountBySubjectResponse(BaseModel):
    subject_id: int
    subject_title: str
    document_count: int

class QuizHistoryResponse(BaseModel):
    attempt_id: int
    quiz_id: int
    quiz_title: str
    subject_title: Optional[str] = None
    total_score: float
    time_start: Optional[datetime] = None
    time_submitted: Optional[datetime] = None

class ProgressChartItem(BaseModel):
    time_submitted: datetime
    total_score: float
    quiz_title: str

class ScoreDistributionResponse(BaseModel):
    excellent: int
    good: int
    fair: int
    average: int
    weak: int
