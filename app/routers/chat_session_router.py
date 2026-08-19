from typing import Optional, List
from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_chat_session_service, get_current_user
from app.core.permissions import require_role
from app.models.user import User
from app.schemas.chat_session import ChatSessionResponse, ChatSessionRequest
from app.services.chat_session_service import ChatSessionService

router = APIRouter(tags=["ChatSession"])


@router.post("/chat-sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def create_chat_session(
        chat_session_request: ChatSessionRequest,
        current_user: User = Depends(get_current_user),
        chat_session_service: ChatSessionService = Depends(get_chat_session_service)
):
    return await chat_session_service.create_chat_session(chat_session_request=chat_session_request,
                                                          user_id=current_user.id)


@router.get("/chat-sessions", response_model=List[ChatSessionResponse], status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def get_chat_sessions_by_user_id(
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        current_user: User = Depends(get_current_user),
        chat_session_service: ChatSessionService = Depends(get_chat_session_service)
):
    params = {
        "limit": limit,
        "offset": offset,
    }
    return await chat_session_service.get_chat_session_by_user_id(user_id=current_user.id, params=params)
