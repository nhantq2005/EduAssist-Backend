from pydantic import BaseModel, ConfigDict


class FlashcardResponse(BaseModel):
    id: int
    front: str
    back: str
    
    model_config = ConfigDict(from_attributes=True)