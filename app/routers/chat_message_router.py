from typing import List
from fastapi import APIRouter, Depends

from app.api.dependencies import get_chat_message_service
from app.core.permissions import require_role
from app.schemas.chat_message import ChatMessageResponse
from app.services.chat_message_service import ChatMessageService

router = APIRouter(tags=["ChatMessage"])

@router.get("/chat-sessions/{chat_session_id}/chat-message", response_model=List[ChatMessageResponse])
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def get_chat_message_by_chat_session_id(
        chat_session_id: int,
        chat_message_service: ChatMessageService = Depends(get_chat_message_service)
):
    return await chat_message_service.get_message_in_session(chat_session_id)