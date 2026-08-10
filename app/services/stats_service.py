from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Document, Subject, Quiz, User
from app.models.user import UserRole


class StatsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_document_by_lecture(self, lecture_id: int) -> int:
        stm = select(func.count(Document.id)).where(Document.lecturer_id == lecture_id)
        total_docs = await self.session.execute(stm)
        return total_docs.scalar()

    async def count_subject_by_lecture(self, lecture_id: int) -> int:
        stm = select(func.count(Subject.id)).where(Subject.lecturer_id == lecture_id)
        total_subjects = await self.session.execute(stm)
        return total_subjects.scalar()

    async def count_quiz_by_subject(self, subject_id: int) -> int:
        stm = select(func.count(Quiz.id)).where(Quiz.subject_id == subject_id)
        total_quizes = await self.session.execute(stm)
        return total_quizes.scalar()

    async def count_lecture(self):
        stm = select(func.count(User.id)).where(User.role == UserRole.LECTURER)
        total_lectures = await self.session.execute(stm)
        return total_lectures.scalar()

    async def count_student(self):
        stm = select(func.count(User.id)).where(User.role == UserRole.STUDENT)
        total_student = await self.session.execute(stm)
        return total_student.scalar()

    async def count_documents_by_subject(self):
        stm = (
            select(
                Subject.id.label("subject_id"),
                Subject.name.label("subject_title"),
                func.count(Document.id).label("document_count")
            )
            .outerjoin(Document, Subject.id == Document.subject_id)
            .group_by(Subject.id, Subject.name)
        )

        result = await self.session.execute(stm)
        return [
            {
                "subject_id": row.subject_id,
                "subject_title": row.subject_title,
                "document_count": row.document_count,
            }
            for row in result
        ]
