from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.document import DocumentResponse


class FlashcardSetResponse(BaseModel):
    id: int
    title: str
    created_date: datetime
    document: DocumentResponse
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)

class FlashcardSetRequest(BaseModel):
    title:str

class GenerateFlashcardSetRequest(BaseModel):
    document_id: int
    title: str