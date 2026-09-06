from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.flashcard import Flashcard


class FlashcardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_flashcards(self, flashcard_set_id):
        stm = select(Flashcard).where(Flashcard.flashcard_set_id == flashcard_set_id)
        result = await self.session.execute(stm)
        return result.scalars().all()
