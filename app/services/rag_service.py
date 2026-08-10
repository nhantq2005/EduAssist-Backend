from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.rag.generate.answer_generator import stream_answer


class RagService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_answer(self, question: str, chat_session_id: int):
        return StreamingResponse(
            stream_answer(question, chat_session_id, self.session),
            media_type="text/event-stream"
        )
