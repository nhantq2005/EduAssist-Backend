from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ChatSessionRequest(BaseModel):
    title: str
    # user_id: int
    # created_date: datetime
    # updated_date: datetime

class ChatSessionUpdate(BaseModel):
    title: str | None = None
    updated_date: datetime | None = None

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_date: datetime
    updated_date: datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)
