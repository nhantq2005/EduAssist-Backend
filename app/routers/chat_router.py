from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.rag.generate.answer_generator import stream_answer
from app.schemas.chat_message import ChatMessageRequest
from app.db.session import get_db

router = APIRouter(tags=["Chat"])

@router.post("/stream")
async def chat_stream(request: ChatMessageRequest, db: AsyncSession = Depends(get_db)):
    return StreamingResponse(
        stream_answer(request.question, request.chat_session_id, db),
        media_type="text/event-stream"
    )