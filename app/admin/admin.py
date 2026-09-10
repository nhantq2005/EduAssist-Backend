from fastapi import FastAPI, Request
from sqladmin import Admin, ModelView, action
from sqladmin.filters import BooleanFilter, StaticValuesFilter
from sqlalchemy import select
from starlette.responses import RedirectResponse
from app.admin.auth import AdminAuth
from app.db.session import engine
from app.models import Document, Question, Quiz
from app.models.subject import Subject
from app.models.user import User, UserRole
from app.db.session import AsyncSessionLocal


class UserAdmin(ModelView, model=User):
    identity = "user"
    name = "Người dùng"
    name_plural = "Quản lý Người dùng"
    column_list = [User.id, User.username, User.name, User.email, User.role, User.is_active]
    column_searchable_list = [User.username, User.email, User.name]
    form_excluded_columns = [User.documents, User.attempt_quizzes, User.subjects,
                             User.chat_sessions, User.flashcard_sets]
    icon = "fa-solid fa-user"

    column_filters = [
        BooleanFilter(User.is_active),
        StaticValuesFilter(User.role, values=[
            ("ADMIN", "Admin"),
            ("LECTURER", "Lecturer"),
            ("STUDENT", "Student")
        ])
    ]

    @action(
        name="toggle_active",
        label="Phê duyệt giảng viên",
        confirmation_message="Bạn có chắc chắn muốn duyệt tài khoản này?",
        add_in_detail=True,
        add_in_list=True,
    )
    async def toggle_active(self, request: Request):
        pks = request.query_params.get("pks", "").split(",")
        if pks:
            async with AsyncSessionLocal() as session:
                for pk in pks:
                    if pk.strip():
                        user = await session.get(User, int(pk))
                        if user:
                            user.is_active = True
                await session.commit()

        referer = request.headers.get("referer")
        if referer:
            return RedirectResponse(referer)
        return RedirectResponse(request.url_for("admin:list", identity=self.identity))

    @action(
        name="toggle_block",
        label="Khóa tài khoản",
        confirmation_message="Bạn có chắc chắn muốn khóa tài khoản của người dùng này?",
        add_in_detail=True,
        add_in_list=True,
    )
    async def toggle_block(self, request: Request):
        pks = request.query_params.get("pks", "").split(",")
        if pks:
            async with AsyncSessionLocal() as session:
                for pk in pks:
                    if pk.strip():
                        user = await session.get(User, int(pk))
                        if user:
                            user.is_active = False
                await session.commit()

        referer = request.headers.get("referer")
        if referer:
            return RedirectResponse(referer)
        return RedirectResponse(request.url_for("admin:list", identity=self.identity))


class SubjectAdmin(ModelView, model=Subject):
    name = "Môn học"
    name_plural = "Quản lý Môn học"
    column_list = [Subject.id, Subject.code, Subject.name, Subject.lecturer_id]
    column_searchable_list = [Subject.code, Subject.name]
    form_excluded_columns = [Subject.documents, Subject.quizzes]
    icon = "fa-solid fa-book"

class DocumentAdmin(ModelView, model=Document):
    name = "Tài liệu"
    name_plural = "Quản lý tài liệu"
    column_list = [Document.title, Document.created_date, Document.process_status, Document.file_name]
    column_searchable_list = [Document.title, Document.created_date]
    readonly_columns = [Document.id, Document.created_date, Document.process_status, Document.file_name]
    form_excluded_columns = [Document.flashcard_sets]
    icon = "fa-solid fa-file-pdf"

class QuizAdmin(ModelView, model=Quiz):
    name = "Bài Quiz"
    name_plural = "Quản lý Quiz"
    column_list = [Quiz.id, Quiz.title, Quiz.subject_id, Quiz.created_date]
    column_searchable_list = [Quiz.title]
    form_excluded_columns = [Quiz.quiz_attempts]
    icon = "fa-solid fa-list-check"

class QuestionAdmin(ModelView, model=Question):
    name = "Câu hỏi"
    name_plural = "Ngân hàng Câu hỏi"
    column_list = [Question.id, Question.quiz_id, Question.question]
    icon = "fa-solid fa-circle-question"
    form_excluded_columns = [Question.user_answers]

def setup_admin(app: FastAPI):
    authentication_backend = AdminAuth(secret_key="super-secret-admin-key")
    admin = Admin(app, engine, title="EduAssist", authentication_backend=authentication_backend)
    admin.add_view(UserAdmin)
    admin.add_view(SubjectAdmin)
    admin.add_view(DocumentAdmin)
    admin.add_view(QuizAdmin)
    admin.add_view(QuestionAdmin)
