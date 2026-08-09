from pydantic import BaseModel
from typing import List


class DocumentCountBySubjectResponse(BaseModel):
    subject_id: int
    subject_title: str
    document_count: int
