from pydantic import BaseModel, ConfigDict, Field


class FlashcardCreate(BaseModel):
    front: str = Field(description="Mặt trước của flashcard (Câu hỏi hoặc thuật ngữ)")
    back: str = Field(description="Mặt sau của flashcard (Đáp án hoặc định nghĩa)")


class FlashcardResponse(BaseModel):
    id: int
    front: str
    back: str
    
    model_config = ConfigDict(from_attributes=True)


class FlashcardList(BaseModel):
    flashcards: list[FlashcardCreate] = Field(description="Danh sách các flashcard được tạo")

