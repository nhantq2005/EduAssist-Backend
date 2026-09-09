import jwt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.admin.admin import setup_admin
from app.core.config import settings
from app.core.websocket import manager
from app.db.session import AsyncSessionLocal
from app.routers import chat_message_router, chat_router, chat_session_router, question_router, quiz_attempt_router, \
    quiz_router, stats_router, subject_router, user_router, flashcard_router
from app.routers.document_router import router as document_router
from app.services.user_service import UserService

app = FastAPI()

settings.configure_cloudinary()

setup_admin(app)


app.include_router(document_router, prefix="/api")
app.include_router(user_router.router, prefix="/api")
app.include_router(subject_router.router, prefix="/api")
app.include_router(question_router.router, prefix="/api")
app.include_router(quiz_router.router, prefix="/api")
app.include_router(chat_router.router, prefix="/api")
app.include_router(stats_router.router, prefix="/api")
app.include_router(chat_message_router.router, prefix="/api")
app.include_router(chat_session_router.router, prefix="/api")
app.include_router(quiz_attempt_router.router, prefix="/api")
app.include_router(flashcard_router.router, prefix="/api")


@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user_id = None

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "AUTH":
                token = data.get("token")
                try:
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                    username = payload.get("sub")
                    async with AsyncSessionLocal() as db:
                        user = await UserService(db).get_user_by_username(username)
                        if user and user.is_active:
                            user_id = user.id
                            await manager.connect(websocket, user_id)
                        else:
                            await websocket.close(code=1008)
                            return
                except Exception:
                    await websocket.close(code=1008)
                    return

    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(user_id)