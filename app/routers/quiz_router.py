from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.api.dependencies import get_quiz_service, get_current_user
from app.core.permissions import require_role
from app.models import User
from app.schemas.quiz import QuizResponse, QuizCreate, QuizUpdate, QuizGenerateRequest
from app.services.quiz_service import QuizService
from app.rag.generate.quiz_generator import generate_quiz_from_topic, QuizData

router = APIRouter(tags=["Quizzes"])


@router.post("/quizzes", response_model=QuizResponse, status_code=201)
@require_role(["ADMIN", "LECTURER"])
async def create_quiz(
        quiz_request: QuizCreate,
        current_user: User = Depends(get_current_user),
        quiz_service: QuizService = Depends(get_quiz_service)
):
    return await quiz_service.create_quiz(quiz_request)

@router.post("/quizzes/generate", response_model=QuizData, status_code=200)
@require_role(["ADMIN", "LECTURER"])
async def generate_quiz_by_ai(
        request: QuizGenerateRequest,
        current_user: User = Depends(get_current_user)
):
    try:
        quiz_data = await generate_quiz_from_topic(request.topic, request.num_questions)
        return quiz_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi sinh trắc nghiệm: {str(e)}")


@router.get("/quizzes", response_model=List[QuizResponse])
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def get_quizzes(
        title: Optional[str] = None,
        subject_id: Optional[int] = None,
        difficulty_level: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        current_user: User = Depends(get_current_user),
        quiz_service: QuizService = Depends(get_quiz_service)
):
    params = {
        "title": title,
        "subject_id": subject_id,
        "difficulty_level": difficulty_level,
        "offset": offset,
        "limit": limit
    }
    return await quiz_service.get_quizzes(params)


@router.get("/subjects/{subject_id}/quizzes", response_model=List[QuizResponse])
async def get_quizzes_by_subject(
        subject_id: int,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0,
        quiz_service: QuizService = Depends(get_quiz_service)
):
    params = {limit: limit, offset: offset}
    quizzes = await quiz_service.get_quiz_by_subject(subject_id, params)
    if not quizzes:
        raise HTTPException(status_code=404, detail="Không tìm thấy quiz nào cho môn học này")
    return quizzes


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: int, quiz_service: QuizService = Depends(get_quiz_service)):
    quiz = await quiz_service.get_quiz_by_id(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz không tồn tại")
    return quiz


@router.put("/quizzes/{quiz_id}", response_model=QuizResponse)
@require_role(["ADMIN", "LECTURER"])
async def update_quiz(
        quiz_id: int,
        quiz_in: QuizUpdate,
        current_user: User = Depends(get_current_user),
        quiz_service: QuizService = Depends(get_quiz_service)
):
    params = quiz_in.model_dump(exclude_unset=True)
    if not params:
        raise HTTPException(status_code=400, detail="Không có dữ liệu để cập nhật")

    updated_quiz = await quiz_service.update_quiz(quiz_id, params)
    if not updated_quiz:
        raise HTTPException(status_code=404, detail="Quiz không tồn tại")
    return updated_quiz


@router.delete("/quizzes/{quiz_id}", status_code=204)
@require_role(["ADMIN", "LECTURER"])
async def delete_quiz(
        quiz_id: int,
        current_user: User = Depends(get_current_user),
        quiz_service: QuizService = Depends(get_quiz_service)
):
    deleted_quiz = await quiz_service.delete_quiz(quiz_id)
    if not deleted_quiz:
        raise HTTPException(status_code=404, detail="Quiz không tồn tại")
