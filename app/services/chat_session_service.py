from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import ChatSession
from app.schemas.chat_session import ChatSessionRequest


class ChatSessionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_chat_session(self, chat_session_request: ChatSessionRequest, user_id: int):
        try:
            session = ChatSession(
                **chat_session_request.model_dump(),
                user_id=user_id
            )
            self.session.add(session)
            await self.session.commit()
            await self.session.refresh(session)
            return session
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Dữ liệu không hợp lệ")


    async def delete_chat_session(self, session_id: int):
        chat_session = await self.session.get(ChatSession, session_id)
        if not chat_session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Không tìm thấy đoạn chat id: {session_id}")
        try:
            await self.session.delete(chat_session)
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Lỗi khi xóa đoạn chat")

    async def get_chat_session_by_user_id(self, user_id: int, params: dict):
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        stm = (
            select(ChatSession)
            .options(selectinload(ChatSession.user))
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_date.desc())
        )
        stm = stm.offset(offset).limit(limit)
        result = await self.session.execute(stm)
        return result.scalars().all()
