from datetime import datetime
from pydantic import BaseModel


class DocumentCountBySubjectResponse(BaseModel):
    subject_id: int
    subject_title: str
    document_count: int

class QuizHistoryResponse(BaseModel):
    attempt_id: int
    quiz_id: int
    quiz_title: str
    subject_title: str | None = None
    total_score: float
    time_start: datetime | None = None
    time_submitted: datetime | None = None

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
