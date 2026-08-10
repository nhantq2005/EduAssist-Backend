from fastapi import APIRouter, Depends
from app.api.dependencies import get_rag_service
from app.schemas.chat_message import ChatMessageRequest
from app.services.rag_service import RagService

router = APIRouter(tags=["Chat"])

@router.post("/chat/stream")
async def chat_stream(request: ChatMessageRequest, rag_service : RagService = Depends(get_rag_service)):
    # return StreamingResponse(
    #     stream_answer(request.question, request.chat_session_id, db),
    #     media_type="text/event-stream"
    # )
    return await rag_service.get_answer(request.question, request.chat_session_id)