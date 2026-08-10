# app/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from app.db.session import get_db
from app.services.chat_message_service import ChatMessageService
from app.services.chat_session_service import ChatSessionService
from app.services.document_service import DocumentService
from app.services.question_service import QuestionService
from app.services.rag_service import RagService
from app.services.stats_service import StatsService
from app.services.subject_service import SubjectService
from app.services.user_service import UserService
from app.services.quiz_service import QuizService
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


# KHOI TAO CAC SERVICE
def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    return DocumentService(db)


def get_subject_service(db: AsyncSession = Depends(get_db)) -> SubjectService:
    return SubjectService(db)


def get_quiz_service(db: AsyncSession = Depends(get_db)) -> QuizService:
    return QuizService(db)


def get_rag_service(db: AsyncSession = Depends(get_db)) -> RagService:
    return RagService(db)


def get_chat_session_service(db: AsyncSession = Depends(get_db)) -> ChatSessionService:
    return ChatSessionService(db)


def get_stats_service(db: AsyncSession = Depends(get_db)) -> StatsService:
    return StatsService(db)

def get_question_service(db: AsyncSession = Depends(get_db))-> QuestionService:
    return QuestionService(db)

def get_chat_message_service(db: AsyncSession = Depends(get_db)) -> ChatMessageService:
    return ChatMessageService(db)



# Dependency 2: Lấy User hiện tại đang đăng nhập từ Token
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        user_service: UserService = Depends(get_user_service)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin (Invalid token)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Giải mã token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

    except jwt.PyJWTError:
        raise credentials_exception

    # Query database thông qua UserService
    # Lưu ý: Bạn cần thêm hàm get_user_by_username vào UserService của bạn nhé
    user = await user_service.get_user_by_username(username)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Tài khoản đã bị khóa")

    return user
