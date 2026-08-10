from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.schemas.quiz_attempt import QuizAttemptCreate
from app.models.quiz_attempt import QuizAttempt


class QuizAttemptService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_quiz_attempt(self, quiz_attempt: QuizAttemptCreate) -> QuizAttempt:
        try:
            self.session.add(quiz_attempt)
            await self.session.commit()
            await self.session.refresh(quiz_attempt)
            return quiz_attempt
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_quiz_attempt_by_id(self, quiz_attempt_id: int) -> QuizAttempt:
        quiz_attempt = await self.session.get(QuizAttempt, quiz_attempt_id)
        return quiz_attempt

    async def get_all_quiz_attempts(self, params:dict):
        limit = params.get('limit', 100)
        offset = params.get('offset', 0)
        stm = select(QuizAttempt).offset(offset).limit(limit)
        result = await self.session.execute(stm)
        return list(result.scalars().all())
