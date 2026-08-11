from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.api.dependencies import get_question_service, get_current_user
from app.core.permissions import require_role
from app.models import User
from app.schemas.question import QuestionRequest, QuestionResponse
from app.services.question_service import QuestionService

router = APIRouter(tags=["Questions"])


# @router.post("/questions", response_model=QuestionResponse)
# @require_role(["ADMIN", "LECTURER"])
# async def create_question(
#         question: QuestionRequest,
#         service: QuestionService = Depends(get_question_service)
# ):
#     return await service.create_question(question_request=question)

@router.post("/questions", response_model=List[QuestionResponse])
@require_role(["ADMIN", "LECTURER"])
async def create_questions(
        questions_request: List[QuestionRequest],
        current_user: User = Depends(get_current_user),
        question_service: QuestionService = Depends(get_question_service)
):
    return await question_service.create_questions(list_questions_request=questions_request)


@router.get("/quiz/{quiz_id}/questions", response_model=List[QuestionResponse])
async def get_questions_by_quiz(
        quiz_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        service: QuestionService = Depends(get_question_service)
):
    params = {"limit": limit, "offset": offset}
    return await service.get_question_by_quiz(quiz_id=quiz_id, params=params)


@router.get("/questions", response_model=List[QuestionResponse])
@require_role(["ADMIN", "LECTURER"])
async def get_questions(
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        service: QuestionService = Depends(get_question_service)
):
    params = {"limit": limit, "offset": offset}
    return await service.get_questions(params=params)


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question_by_id(
        question_id: int,
        service: QuestionService = Depends(get_question_service)
):
    db_question = await service.get_question_by_id(question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi")
    return db_question


@router.put("/questions/{question_id}", response_model=QuestionResponse)
@require_role(["ADMIN", "LECTURER"])
async def update_question(
        question_id: int,
        question: QuestionRequest,
        service: QuestionService = Depends(get_question_service)
):
    db_question = await service.update_question(question_id=question_id, question_request=question)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi")
    return db_question


@router.delete("/questions/{question_id}")
@require_role(["ADMIN", "LECTURER"])
async def delete_question(
        question_id: int,
        service: QuestionService = Depends(get_question_service)
):
    success = await service.delete_question(question_id=question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi")
    return {"message": "Xóa câu hỏi thành công"}
