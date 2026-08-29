from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Document, Quiz, Subject, User
from app.models.user import UserRole


class StatsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_document_by_lecture(self, lecture_id: int):
        stm = select(func.count(Document.id)).where(Document.lecturer_id == lecture_id)
        total_docs = await self.session.execute(stm)
        return total_docs.scalar()

    async def count_subject_by_lecture(self, lecture_id: int):
        stm = select(func.count(Subject.id)).where(Subject.lecturer_id == lecture_id)
        total_subjects = await self.session.execute(stm)
        return total_subjects.scalar()

    async def count_quiz_by_subject(self, subject_id: int):
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

    async def get_student_average_score(self, student_id: int):
        from app.models.quiz_attempt import QuizAttempt
        stm = select(func.avg(QuizAttempt.total_score)).where(
            QuizAttempt.user_id == student_id,
            QuizAttempt.is_completed == True
        )
        result = await self.session.execute(stm)
        avg_score = result.scalar()
        return float(avg_score) if avg_score is not None else 0.0

    async def get_student_quiz_history(self, student_id: int):
        from app.models.quiz_attempt import QuizAttempt
        stm = (
            select(
                QuizAttempt.id.label("attempt_id"),
                Quiz.id.label("quiz_id"),
                Quiz.title.label("quiz_title"),
                Subject.name.label("subject_title"),
                QuizAttempt.total_score,
                QuizAttempt.time_start,
                QuizAttempt.time_submitted
            )
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
            .outerjoin(Subject, Quiz.subject_id == Subject.id)
            .where(
                QuizAttempt.user_id == student_id,
                QuizAttempt.is_completed == True
            )
            .order_by(QuizAttempt.time_submitted.desc())
        )
        result = await self.session.execute(stm)
        return [
            {
                "attempt_id": row.attempt_id,
                "quiz_id": row.quiz_id,
                "quiz_title": row.quiz_title,
                "subject_title": row.subject_title,
                "total_score": float(row.total_score),
                "time_start": row.time_start,
                "time_submitted": row.time_submitted
            }
            for row in result
        ]

    async def get_student_progress_chart(self, student_id: int):
        from app.models.quiz_attempt import QuizAttempt
        stm = (
            select(
                QuizAttempt.time_submitted,
                QuizAttempt.total_score,
                Quiz.title.label("quiz_title")
            )
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
            .where(
                QuizAttempt.user_id == student_id,
                QuizAttempt.is_completed == True,
                QuizAttempt.time_submitted != None
            )
            .order_by(QuizAttempt.time_submitted.asc())
        )
        result = await self.session.execute(stm)
        return [
            {
                "time_submitted": row.time_submitted,
                "total_score": float(row.total_score),
                "quiz_title": row.quiz_title
            }
            for row in result
        ]

    async def get_student_score_distribution(self, student_id: int):
        from app.models.quiz_attempt import QuizAttempt
        stm = select(QuizAttempt.total_score).where(
            QuizAttempt.user_id == student_id,
            QuizAttempt.is_completed == True
        )
        result = await self.session.execute(stm)
        scores = [float(row[0]) for row in result]
        
        distribution = {
            "excellent": 0,
            "good": 0,
            "fair": 0,
            "average": 0,
            "weak": 0
        }
        for score in scores:
            if score >= 9.0:
                distribution["excellent"] += 1
            elif score >= 8.0:
                distribution["good"] += 1
            elif score >= 6.5:
                distribution["fair"] += 1
            elif score >= 5.0:
                distribution["average"] += 1
            else:
                distribution["weak"] += 1
                
        return distribution
