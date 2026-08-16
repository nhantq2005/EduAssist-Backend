from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from app.api.dependencies import get_quiz_service, get_current_user, get_question_service
from app.core.permissions import require_role
from app.models import User
from app.schemas.quiz import QuizResponse, QuizCreate, QuizUpdate, QuizGenerateRequest
from app.services.quiz_service import QuizService
from app.rag.generate.quiz_generator import QuizData
from app.services.question_service import QuestionService

router = APIRouter(tags=["Quizzes"])


@router.post("/quizzes", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
@require_role(["ADMIN", "LECTURER"])
async def create_quiz(
        quiz_request: QuizCreate,
        current_user: User = Depends(get_current_user),
        quiz_service: QuizService = Depends(get_quiz_service)
):
    return await quiz_service.create_quiz(quiz_request, current_user.id)


@router.post("/quizzes/generate", response_model=QuizData, status_code=status.HTTP_201_CREATED)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def generate_quiz_by_ai(
        request: QuizGenerateRequest,
        current_user: User = Depends(get_current_user),
        quiz_service: QuizService = Depends(get_quiz_service),
        question_service: QuestionService = Depends(get_question_service)
):
    try:
        return await quiz_service.generate_and_save_quiz(request, current_user.id, question_service)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/quizzes", response_model=List[QuizResponse], status_code=status.HTTP_200_OK)
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
    return await quiz_service.get_quizzes(params, current_user.id, current_user.role)


@router.get("/subjects/{subject_id}/quizzes", response_model=List[QuizResponse], status_code=status.HTTP_200_OK)
async def get_quizzes_by_subject(
        subject_id: int,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0,
        quiz_service: QuizService = Depends(get_quiz_service)
):
    params = {limit: limit, offset: offset}
    quizzes = await quiz_service.get_quiz_by_subject(subject_id, params)
    if not quizzes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy quiz nào cho môn học này")
    return quizzes


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse, status_code=status.HTTP_200_OK)
async def get_quiz(quiz_id: int, quiz_service: QuizService = Depends(get_quiz_service)):
    quiz = await quiz_service.get_quiz_by_id(quiz_id)
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz không tồn tại")
    return quiz


@router.put("/quizzes/{quiz_id}", response_model=QuizResponse, status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def update_quiz(
        quiz_id: int,
        quiz_in: QuizUpdate,
        current_user: User = Depends(get_current_user),
        quiz_service: QuizService = Depends(get_quiz_service)
):
    quiz = await quiz_service.get_quiz_by_id(quiz_id)
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz không tồn tại")

    if current_user.role != "ADMIN" and quiz.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền sửa bài quiz này")

    params = quiz_in.model_dump(exclude_unset=True)
    if not params:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không có dữ liệu để cập nhật")

    updated_quiz = await quiz_service.update_quiz(quiz_id, params)
    if not updated_quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz không tồn tại")
    return updated_quiz


@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role(["ADMIN", "LECTURER"])
async def delete_quiz(
        quiz_id: int,
        current_user: User = Depends(get_current_user),
        quiz_service: QuizService = Depends(get_quiz_service)
):
    quiz = await quiz_service.get_quiz_by_id(quiz_id)
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz không tồn tại")

    if current_user.role != "ADMIN" and quiz.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền xóa bài quiz này")

    deleted_quiz = await quiz_service.delete_quiz(quiz_id)
    if not deleted_quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz không tồn tại")
