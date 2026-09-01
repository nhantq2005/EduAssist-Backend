from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_user, get_question_service, get_quiz_service
from app.core.permissions import require_role
from app.models import User
from app.schemas.question import QuestionRequest, QuestionResponse
from app.services.question_service import QuestionService
from app.services.quiz_service import QuizService

router = APIRouter(tags=["Questions"])


# @router.post("/questions", response_model=QuestionResponse)
# @require_role(["ADMIN", "LECTURER"])
# async def create_question(
#         question: QuestionRequest,
#         service: QuestionService = Depends(get_question_service)
# ):
#     return await service.create_question(question_request=question)

@router.post("/questions", response_model=list[QuestionResponse], status_code=status.HTTP_201_CREATED)
@require_role(["ADMIN", "LECTURER"])
async def create_questions(
        questions_request: list[QuestionRequest],
        current_user: User = Depends(get_current_user),
        question_service: QuestionService = Depends(get_question_service),
        quiz_service: QuizService = Depends(get_quiz_service)
):
    if not questions_request:
        return []
    quiz_id = questions_request[0].quiz_id
    if not quiz_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vui lòng cung cấp quiz_id")

    quiz = await quiz_service.get_quiz_by_id(quiz_id=quiz_id)
    if not quiz:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz không tồn tại")

    if current_user.role != "ADMIN" and quiz.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền thêm câu hỏi vào bài quiz")

    return await question_service.create_questions(list_questions_request=questions_request)


@router.get("/quizzes/{quiz_id}/questions", response_model=list[QuestionResponse], status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def get_questions_by_quiz(
        quiz_id: int,
        limit: int | None = None,
        offset: int | None = None,
        current_user: User = Depends(get_current_user),
        service: QuestionService = Depends(get_question_service)
):
    params = {"limit": limit, "offset": offset}
    return await service.get_question_by_quiz(quiz_id=quiz_id, params=params)


@router.get("/questions", response_model=list[QuestionResponse], status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER"])
async def get_questions(
        limit: int | None = None,
        offset: int | None = None,
        current_user: User = Depends(get_current_user),
        service: QuestionService = Depends(get_question_service)
):
    params = {"limit": limit, "offset": offset}
    return await service.get_questions(params=params)


@router.get("/questions/{question_id}", response_model=QuestionResponse, status_code=status.HTTP_200_OK)
async def get_question_by_id(
        question_id: int,
        service: QuestionService = Depends(get_question_service)
):
    db_question = await service.get_question_by_id(question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi")
    return db_question


@router.put("/questions/{question_id}", response_model=QuestionResponse, status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def update_question(
        question_id: int,
        question: QuestionRequest,
        current_user: User = Depends(get_current_user),
        service: QuestionService = Depends(get_question_service),
        quiz_service: QuizService = Depends(get_quiz_service)
):
    db_question = await service.get_question_by_id(question_id=question_id)
    if not db_question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu hỏi")
    
    quiz = await quiz_service.get_quiz_by_id(quiz_id=db_question.quiz_id)
    if quiz and current_user.role != "ADMIN" and quiz.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền sửa câu hỏi này")

    updated_question = await service.update_question(question_id=question_id, question_request=question)
    return updated_question


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def delete_question(
        question_id: int,
        current_user: User = Depends(get_current_user),
        service: QuestionService = Depends(get_question_service),
        quiz_service: QuizService = Depends(get_quiz_service)
):
    db_question = await service.get_question_by_id(question_id=question_id)
    if not db_question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu hỏi")
    
    quiz = await quiz_service.get_quiz_by_id(quiz_id=db_question.quiz_id)
    if quiz and current_user.role != "ADMIN" and quiz.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền xóa câu hỏi")

    success = await service.delete_question(question_id=question_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu hỏi")
    return {"message": "Xóa câu hỏi thành công"}
