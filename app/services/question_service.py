from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.option import Option
from app.models.question import Question
from app.schemas.question import QuestionRequest


class QuestionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_question_by_id(self, question_id: int):
        result = await self.session.execute(
            select(Question).options(selectinload(Question.options)).where(Question.id == question_id))
        return result.scalars().first()

    async def get_questions(self, params: dict):
        skip = params.get("skip", 0)
        limit = params.get("limit", 100)
        result = await self.session.execute(
            select(Question).options(selectinload(Question.options)).offset(skip).limit(limit))
        return result.scalars().all()

    async def create_question(self, question_request: QuestionRequest) -> Question:
        question_data = question_request.model_dump(exclude={"options"})
        db_question = Question(**question_data)
        self.session.add(db_question)
        await self.session.flush()

        for opt in question_request.options:
            opt_data = opt.model_dump(exclude={"question_id"})
            db_option = Option(**opt_data, question_id=db_question.id)
            self.session.add(db_option)

        await self.session.commit()
        result = await self.session.execute(
            select(Question).options(selectinload(Question.options)).where(Question.id == db_question.id)
        )
        return result.scalars().first()

    async def create_questions(self, list_questions_request: list[QuestionRequest]):
        questions = []
        for question_request in list_questions_request:
            question_data = question_request.model_dump(exclude={"options"})
            db_question = Question(**question_data)
            self.session.add(db_question)
            questions.append((db_question, question_request.options))

        await self.session.flush()

        for db_question, options in questions:
            for opt in options:
                opt_data = opt.model_dump(exclude={"question_id"})
                db_option = Option(**opt_data, question_id=db_question.id)
                self.session.add(db_option)

        await self.session.commit()

        question_ids = [q[0].id for q in questions]
        result = await self.session.execute(
            select(Question)
            .options(selectinload(Question.options))
            .where(Question.id.in_(question_ids))
        )
        return result.scalars().all()


    async def get_question_by_quiz(self, quiz_id: int, params:dict):
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        stm = select(Question).options(selectinload(Question.options)).where(Question.quiz_id == quiz_id).order_by(Question.id)
        stm = stm.limit(limit).offset(offset)
        result = await self.session.execute(stm)
        return result.scalars().all()

    async def update_question(self, question_id: int, question_request: QuestionRequest) -> Question | None:
        db_question = await self.get_question_by_id(question_id)
        if db_question:
            update_data = question_request.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if key != "options":
                    setattr(db_question, key, value)

            if "options" in update_data:
                existing_options = {opt.id: opt for opt in db_question.options}
                
                for opt_req in question_request.options:
                    if opt_req.id and opt_req.id in existing_options:
                        # CAP NHAT OPT
                        existing_opt = existing_options.pop(opt_req.id)
                        existing_opt.content = opt_req.content
                        existing_opt.is_correct = opt_req.is_correct
                    else:
                        # TAO OPT MOI NEU CHUA CO
                        new_opt = Option(
                            content=opt_req.content, 
                            is_correct=opt_req.is_correct, 
                            question_id=question_id
                        )
                        self.session.add(new_opt)
                
                # XOA OPT KHONG DUOC CAP NHAT
                for opt_to_delete in existing_options.values():
                    await self.session.delete(opt_to_delete)
            
            await self.session.commit()
            await self.session.refresh(db_question)

            result = await self.session.execute(
                select(Question).options(selectinload(Question.options)).where(Question.id == question_id))
            return result.scalars().first()
        return db_question

    async def delete_question(self, question_id: int):
        db_question = await self.get_question_by_id(question_id)
        if db_question:
            await self.session.delete(db_question)
            await self.session.commit()
            return True
        return False
