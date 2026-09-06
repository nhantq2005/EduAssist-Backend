from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_user, get_quiz_attempt_service
from app.core.permissions import require_role
from app.models import User
from app.schemas.quiz_attempt import (
    QuizAttemptDetailResponse,
    QuizAttemptResponse,
    QuizSubmitRequest,
)
from app.services.quiz_attempt_service import QuizAttemptService

router = APIRouter(tags=["Quiz Attempts"])


@router.post("/quizzes/{quiz_id}/submit", response_model=QuizAttemptResponse, status_code=status.HTTP_201_CREATED)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def submit_quiz(
        quiz_id: int,
        request: QuizSubmitRequest,
        current_user: User = Depends(get_current_user),
        quiz_attempt_service: QuizAttemptService = Depends(get_quiz_attempt_service),
):
    try:
        attempt = await quiz_attempt_service.submit_quiz(
            user_id=current_user.id,
            quiz_id=quiz_id,
            request_data=request
        )
        return attempt
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/quiz-attempts/me", response_model=list[QuizAttemptResponse], status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def get_my_quiz_attempts(
        limit: int = None,
        offset: int = None,
        current_user: User = Depends(get_current_user),
        quiz_attempt_service: QuizAttemptService = Depends(get_quiz_attempt_service),
):
    params = {"limit": limit, "offset": offset}
    try:
        attempts = await quiz_attempt_service.get_user_quiz_attempts(
            user_id=current_user.id,
            params=params
        )
        return attempts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/quiz-attempts/{attempt_id}", response_model=QuizAttemptDetailResponse, status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def get_quiz_attempt_detail(
        attempt_id: int,
        current_user: User = Depends(get_current_user),
        quiz_attempt_service: QuizAttemptService = Depends(get_quiz_attempt_service),
):
    try:
        attempt = await quiz_attempt_service.get_quiz_attempt_by_id(quiz_attempt_id=attempt_id)
        if not attempt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài làm")

        if current_user.role == "STUDENT" and attempt.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền xem bài làm")

        return attempt
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
