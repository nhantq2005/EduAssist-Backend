from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.rag.generate.flashcard_generator import generate_from_chromadb
from app.models import FlashcardSet
from app.schemas.flashcard_set import FlashcardSetRequest


class FlashcardSetService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_flashcard_set(self, document_id: int, user_id: int, title: str) -> FlashcardSet:
        flashcard_set = await generate_from_chromadb(
            db=self.session,
            document_id=document_id,
            user_id=user_id,
            title=title
        )
        # Fetch again with relations to satisfy response model
        result = await self.session.execute(
            select(FlashcardSet).options(selectinload(FlashcardSet.document)).where(FlashcardSet.id == flashcard_set.id)
        )
        return result.scalar_one()

    async def delete_flashcard_set(self, flashcard_set_id: int, user_id: int) -> bool:
        try:
            flashcard_set = await self.session.get(FlashcardSet, flashcard_set_id)
            if not flashcard_set:
                raise Exception(f"Không tìm thấy tập flashcard: {flashcard_set_id}")
            if user_id != flashcard_set.user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Bạn không có quyền xóa tập flashcard này")
            await self.session.delete(flashcard_set)
            await self.session.commit()
            return True
        except Exception:
            return False

    async def update_flashcard_set(self, flashcard_set_id: int, flashcard_set_request: FlashcardSetRequest, user_id: int) -> FlashcardSet:
        flashcard_set = await self.session.get(FlashcardSet, flashcard_set_id, options=[selectinload(FlashcardSet.document)])
        if not flashcard_set:
            raise Exception(f"Không tìm thấy tập flashcard: {flashcard_set_id}")
        if user_id != flashcard_set.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền chỉnh sửa tập flashcard này")
        flashcard_set.title = flashcard_set_request.title
                
        try:
            await self.session.commit()
            await self.session.refresh(flashcard_set)
            return flashcard_set
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_flashcard_set(self, user_id: int, params: dict) -> list[FlashcardSet]:
        offset = params.get('offset', 0)
        limit = params.get('limit', 100)
        stm = select(FlashcardSet).options(selectinload(FlashcardSet.document)).where(FlashcardSet.user_id == user_id)
        stm = stm.offset(offset).limit(limit)
        result = await self.session.execute(stm)
        return list(result.scalars().all())