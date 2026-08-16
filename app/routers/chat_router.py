from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_rag_service, get_current_user
from app.core.permissions import require_role
from app.models.user import User, UserRole
from app.schemas.chat_message import ChatMessageRequest
from app.services.rag_service import RagService

router = APIRouter(tags=["Chat"])

@router.post("/chat/stream", status_code=status.HTTP_201_CREATED)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def chat_stream(
    request: ChatMessageRequest, 
    current_user: User = Depends(get_current_user),
    rag_service : RagService = Depends(get_rag_service)
):
    # return StreamingResponse(
    #     stream_answer(request.question, request.chat_session_id, db),
    #     media_type="text/event-stream"
    # )
    return await rag_service.get_answer(request.question, request.chat_session_id)