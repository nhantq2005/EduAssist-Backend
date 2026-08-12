from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.subject import Subject
from app.schemas.subject import SubjectRequest


class SubjectService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_subject_by_id(self, subject_id: int):
        stm = select(Subject).options(selectinload(Subject.lecturer), selectinload(Subject.documents)).where(
            Subject.id == subject_id)
        result = await self.session.execute(stm)
        return result.scalar_one_or_none()

    async def get_subjects(self, params: dict):
        stm = (select(Subject).options(selectinload(Subject.lecturer)))

        if params.get("name") is not None:
            stm = stm.where(Subject.name.ilike(f"%{params['name']}%"))

        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        stm = stm.offset(offset).limit(limit)
        result = await self.session.execute(stm)
        return result.scalars().all()

    async def create_subject(self, subject_request: SubjectRequest,lecturer_id: int):
        try:
            subject = Subject(**subject_request.model_dump())
            subject.lecturer_id = lecturer_id
            self.session.add(subject)
            await self.session.commit()
            return await self.get_subject_by_id(subject.id)
        except Exception as e:
            await self.session.rollback()
            raise e

    async def update_subject(self, subject_id: int, subject_request: SubjectRequest, lecturer_id: int):
        try:
            subject = await self.get_subject_by_id(subject_id)
            if subject:
                update_data = subject_request.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(subject, key, value)
                subject.lecturer_id = lecturer_id
                await self.session.commit()
                await self.session.refresh(subject)
            return subject
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete_subject(self, subject_id: int):
        db_subject = await self.get_subject_by_id(subject_id)
        if db_subject:
            await self.session.delete(db_subject)
            await self.session.commit()
            return True
        return False

    async def get_subjects_by_lecturer(self, lecturer_id: int, params: dict):
        stm = (select(Subject).options(selectinload(Subject.lecturer)).where(Subject.lecturer_id == lecturer_id))
        if params.get("name") is not None:
            stm = stm.where(Subject.name.ilike(f"%{params['name']}%"))
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        stm = stm.offset(offset).limit(limit)
        result = await self.session.execute(stm)
        return result.scalars().all()
