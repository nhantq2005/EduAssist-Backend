from fastapi import FastAPI

from app.routers import user_router, subject_router, question_router, option_router, quiz_router, chat_router, \
    stats_router
from app.routers.document_router import router as document_router

from app.core.config import settings
from app.admin.admin import setup_admin

app = FastAPI()

settings.configure_cloudinary()

setup_admin(app)


app.include_router(document_router, prefix="/api")
app.include_router(user_router.router, prefix="/api")
app.include_router(subject_router.router, prefix="/api")
app.include_router(question_router.router, prefix="/api")
# app.include_router(option.router, prefix="/api")
app.include_router(quiz_router.router, prefix="/api")
app.include_router(chat_router.router, prefix="/api/chat")
app.include_router(stats_router.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


