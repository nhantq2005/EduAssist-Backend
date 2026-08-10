from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.models import ChatSession
from fastapi import HTTPException, status

class ChatSessionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_chat_session(self, user_id: int, title: str = "Đoạn chat mới"):
        new_session = ChatSession(
            user_id=user_id,
            title=title,
            created_date=datetime.now(),
            updated_date=datetime.now()
        )
        self.session.add(new_session)
        await self.session.commit()
        await self.session.refresh(new_session)
        return new_session

    async def delete_chat_session(self, session_id: int):
        chat_session = await self.session.get(ChatSession, session_id)
        if not chat_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy đoạn chat với id: {session_id}"
            )
        try:
            await self.session.delete(chat_session)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi xóa đoạn chat: {str(e)}"
            )