from fastapi import FastAPI
from sqladmin.filters import BooleanFilter, StaticValuesFilter
from sqlalchemy import select

from app.admin.auth import AdminAuth
from sqladmin import Admin, ModelView
from app.db.session import engine
from app.models import Document
from app.models.user import User, UserRole
from app.models.subject import Subject


class UserAdmin(ModelView, model=User):
    identity = "user"
    name = "Người dùng"
    name_plural = "Quản lý Người dùng"
    column_list = [User.id, User.username, User.name, User.email, User.role, User.is_active]
    column_searchable_list = [User.username, User.email, User.name]
    form_excluded_columns = [User.documents, User.attempt_quizzes, User.subjects,
                             User.notification_reads, User.chat_sessions]
    icon = "fa-solid fa-user"

    # THÊM BỘ LỌC VÀO ĐÂY:
    column_filters = [
        BooleanFilter(User.is_active),
        StaticValuesFilter(User.role, values=[
            ("ADMIN", "Admin"),
            ("LECTURER", "Lecturer"),
            ("STUDENT", "Student")
        ])
    ]


class SubjectAdmin(ModelView, model=Subject):
    name = "Môn học"
    name_plural = "Quản lý Môn học"
    column_list = [Subject.id, Subject.code, Subject.name, Subject.lecturer_id]
    column_searchable_list = [Subject.code, Subject.name]
    form_excluded_columns = [Subject.notifications, Subject.documents, Subject.quizzes]
    icon = "fa-solid fa-book"

    form_args = dict(
        lecturer=dict(
            query_factory=lambda: select(User).where(User.role == UserRole.LECTURER)
        )
    )

class DocumentAdmin(ModelView, model=Document):
    name = "Tài liệu"
    name_plural = "Quản lý tài liệu"
    column_list = [Document.title, Document.created_date, Document.process_status, Document.file_name]
    column_searchable_list = [Document.title, Document.created_date]
    icon = "fa-solid fa-file-pdf"

def setup_admin(app: FastAPI):
    authentication_backend = AdminAuth(secret_key="super-secret-admin-key")
    admin = Admin(
        app, 
        engine, 
        title="EduAssist",
        authentication_backend=authentication_backend
    )
    admin.add_view(UserAdmin)
    admin.add_view(SubjectAdmin)
    admin.add_view(DocumentAdmin)
