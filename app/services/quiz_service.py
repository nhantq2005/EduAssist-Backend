from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Quiz
from app.schemas.quiz import QuizCreate


class QuizService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_quiz(self, quiz_request: QuizCreate) -> Quiz:
        try:
            quiz = Quiz(**quiz_request.model_dump())
            self.session.add(quiz)
            await self.session.commit()
            await self.session.refresh(quiz)
            return quiz
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def get_quizzes(self, params: dict) -> list[Quiz]:
        stm = select(Quiz)

        if params.get('title') is not None:
            stm = stm.where(Quiz.title.ilike(f"%{params['title']}%"))
        if params.get('subject_id') is not None:
            stm = stm.where(Quiz.subject_id == params['subject_id'])
        if params.get('difficulty_level') is not None:
            stm = stm.where(Quiz.difficulty_level == params['difficulty_level'])

        offset = params.get('offset', 0)
        limit = params.get('limit', 100)
        stm = stm.offset(offset).limit(limit)

        result = await self.session.execute(stm)

        return list(result.scalars().all())

    async def get_quiz_by_subject(self, subject_id: int, params: dict):
        limit = params.get('limit', 100)
        offset = params.get('offset', 0)
        stm = select(Quiz).where(Quiz.subject_id == subject_id).offset(offset).limit(limit)
        result = await self.session.execute(stm)
        return list(result.scalars().all())

    async def get_quiz_by_id(self, quiz_id: int) -> Quiz:
        quiz = await self.session.get(Quiz, quiz_id)
        return quiz

    async def update_quiz(self, quiz_id: int, params: dict) -> Quiz:
        quiz = await self.session.get(Quiz, quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy quiz với id: {quiz_id}")

        try:
            for key, value in params.items():
                setattr(quiz, key, value)

            await self.session.commit()
            await self.session.refresh(quiz)
            return quiz
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete_quiz(self, quiz_id: int) -> Quiz:
        quiz = await self.session.get(Quiz, quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy quiz với id: {quiz_id}")

        try:
            await self.session.delete(quiz)
            await self.session.commit()
            return quiz
        except Exception as e:
            await self.session.rollback()
            raise e
