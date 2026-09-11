from pydantic import BaseModel

class DocumentCountBySubjectResponse(BaseModel):
    subject_id: int
    subject_title: str
    document_count: int

class ScoreDistributionItem(BaseModel):
    label: str
    value: int
