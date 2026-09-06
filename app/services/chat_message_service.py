from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ChatMessage
from app.schemas.chat_message import ChatMessageCreate
from sqlalchemy import select


class ChatMessageService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_chat_message(self, chat_message_create: ChatMessageCreate):
        try:
            message = ChatMessage(**chat_message_create.model_dump())
            self.session.add(message)
            await self.session.commit()
        except Exception as e:
            print("Lỗi khi lưu:", e)
            await self.session.rollback()

    async def get_message_in_session(self, session_id: int):
        stm = select(ChatMessage).where(ChatMessage.chat_session_id == session_id).order_by(ChatMessage.id)
        result = await self.session.execute(stm)
        return result.scalars().all()
