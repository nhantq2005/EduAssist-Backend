from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from app.models.quiz import Quiz
from app.models.option import Option
from app.models.question import Question
from app.models.quiz_attempt import QuizAttempt
from app.models.user_answer import UserAnswer
from app.schemas.quiz_attempt import QuizAttemptCreate
from sqlalchemy.orm import selectinload


class QuizAttemptService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_quiz_attempt(self, quiz_attempt: QuizAttemptCreate):
        try:
            db_attempt = QuizAttempt(**quiz_attempt.model_dump())
            self.session.add(db_attempt)
            await self.session.commit()
            await self.session.refresh(db_attempt)
            return db_attempt
        except Exception:
            await self.session.rollback()
            raise

    async def get_quiz_attempt_by_id(self, quiz_attempt_id: int):
        from sqlalchemy.orm import selectinload

        stm = (
            select(QuizAttempt)
            .where(QuizAttempt.id == quiz_attempt_id)
            .options(
                selectinload(QuizAttempt.quiz),
                selectinload(QuizAttempt.user_answers)
                .selectinload(UserAnswer.question)
                .selectinload(Question.options),
                selectinload(QuizAttempt.user_answers).selectinload(UserAnswer.option),
            )
        )
        result = await self.session.execute(stm)
        return result.scalar_one_or_none()

    async def get_all_quiz_attempts(self, params: dict):

        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        stm = select(QuizAttempt).options(selectinload(QuizAttempt.quiz)).offset(offset).limit(limit)
        result = await self.session.execute(stm)
        return list(result.scalars().all())

    async def get_user_quiz_attempts(
            self, user_id: int, params: dict
    ):
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        stm = (
            select(QuizAttempt)
            .options(selectinload(QuizAttempt.quiz))
            .where(QuizAttempt.user_id == user_id)
            .offset(offset)
            .limit(limit)
            .order_by(QuizAttempt.created_date.desc())
        )
        result = await self.session.execute(stm)
        return list(result.scalars().all())

    async def submit_quiz(self, user_id: int, quiz_id: int, request_data):
        stm_quiz = select(Quiz).where(Quiz.id == quiz_id)
        result_quiz = await self.session.execute(stm_quiz)
        if not result_quiz.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài quiz này")

        answers = request_data.answers
        total_questions = len(answers)
        correct_count = 0
        option_ids = [ans.selected_option_id for ans in answers if ans.selected_option_id]
        options_dict = {}
        if option_ids:
            stm_options = select(Option).where(Option.id.in_(option_ids))
            result_options = await self.session.execute(stm_options)
            options = result_options.scalars().all()
            options_dict = {opt.id: opt for opt in options}

        time_start_naive = request_data.time_start.replace(tzinfo=None) if hasattr(request_data,
                                                                                   'time_start') and request_data.time_start else None

        quiz_attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            time_start=time_start_naive,
            time_submitted=datetime.now(),
            total_questions=total_questions,
            total_score=0.0,
            correct_count=0,
            is_completed=True
        )
        self.session.add(quiz_attempt)
        await self.session.flush()

        for ans in answers:
            selected_option = options_dict.get(ans.selected_option_id)

            is_correct = selected_option.is_correct if selected_option else False
            if is_correct:
                correct_count += 1

            user_answer = UserAnswer(
                quiz_attempt_id=quiz_attempt.id,
                question_id=ans.question_id,
                option_id=ans.selected_option_id,
                is_correct=is_correct,
            )
            self.session.add(user_answer)

        score = (correct_count / total_questions * 10) if total_questions > 0 else 0.0

        quiz_attempt.correct_count = correct_count
        quiz_attempt.total_score = score

        await self.session.commit()
        await self.session.refresh(quiz_attempt)

        return quiz_attempt
