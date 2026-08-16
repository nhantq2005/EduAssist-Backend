from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Quiz
from app.models.quiz import SourceType
from app.schemas.quiz import QuizCreate, QuizGenerateRequest
from app.rag.generate.quiz_generator import generate_quiz_from_topic, QuizData
from app.services.question_service import QuestionService


class QuizService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_quiz(self, quiz_request: QuizCreate, user_id: int) -> Quiz:
        try:
            data = quiz_request.model_dump()
            data["created_by"] = user_id
            quiz = Quiz(**data)
            self.session.add(quiz)
            await self.session.commit()
            await self.session.refresh(quiz)
            return quiz
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def generate_and_save_quiz(self, request: QuizGenerateRequest, user_id: int, question_service: QuestionService) -> QuizData:
        try:
            quiz_data = await generate_quiz_from_topic(request.topic, request.num_questions)
            quiz_create = QuizCreate(
                title=f"AI Quiz: {request.topic}",
                description=f"Bài trắc nghiệm chủ đề: {request.topic}",
                source_type=SourceType.AI_GENERATED,
                difficulty_level=request.difficulty_level,
                subject_id=request.subject_id,
                is_public=request.is_public
            )
            quiz = await self.create_quiz(quiz_create, user_id)
            for question in quiz_data.questions:
                question.quiz_id = quiz.id
            await question_service.create_questions(quiz_data.questions)
            return quiz_data
        except Exception as e:
            raise Exception(f"Lỗi khi sinh trắc nghiệm: {str(e)}")

    async def get_quizzes(self, params: dict, user_id: int, role: str) -> list[Quiz]:
        stm = select(Quiz)

        if role == "STUDENT":
            stm = stm.where(or_(Quiz.is_public == True, Quiz.created_by == user_id))
        elif role == "LECTURER":
            stm = stm.where(Quiz.created_by == user_id)

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
