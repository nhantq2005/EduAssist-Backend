from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.admin.admin import setup_admin
from app.core.config import settings
from app.core.websocket import manager
from app.routers import chat_message_router, chat_router, chat_session_router, question_router, quiz_attempt_router, quiz_router, stats_router, subject_router, user_router
from app.routers.document_router import router as document_router

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


@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
