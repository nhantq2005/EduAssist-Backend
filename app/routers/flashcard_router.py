from fastapi import APIRouter, Depends, status, BackgroundTasks
from app.api.dependencies import get_current_user, get_flashcard_service, get_flashcard_set_service
from app.core.permissions import require_role
from app.models import User
from app.schemas.flashcard import FlashcardResponse
from app.schemas.flashcard_set import FlashcardSetRequest, FlashcardSetResponse, GenerateFlashcardSetRequest
from app.services.flashcard_service import FlashcardService
from app.services.flashcard_set_service import FlashcardSetService, background_generate_flashcard_set
from fastapi import HTTPException

from app.services.quiz_service import background_generate_quiz

router = APIRouter(tags=['Flashcard'])


@router.get('/flashcard-sets/{flashcard_set_id}/flashcards', response_model=list[FlashcardResponse],
            status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def get_flashcards(
        flashcard_set_id: int,
        current_user: User = Depends(get_current_user),
        service: FlashcardService = Depends(get_flashcard_service)
):
    return await service.get_flashcards(flashcard_set_id=flashcard_set_id)


@router.get('/flashcard-sets', response_model=list[FlashcardSetResponse], status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def get_flashcard_sets(
        limit: int | None = None,
        offset: int | None = None,
        current_user: User = Depends(get_current_user),
        service: FlashcardSetService = Depends(get_flashcard_set_service)
):
    params = {"limit": limit, "offset": offset}
    return await service.get_flashcard_set(user_id=current_user.id, params=params)


@router.post('/flashcard-sets/generate', status_code=status.HTTP_202_ACCEPTED)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def generate_flashcard_set(
        generate_flashcard_set_request: GenerateFlashcardSetRequest,
        background_tasks: BackgroundTasks,
        current_user: User = Depends(get_current_user)
):
    try:
        background_tasks.add_task(
            background_generate_flashcard_set,
            document_id=generate_flashcard_set_request.document_id,
            user_id=current_user.id,
            title=generate_flashcard_set_request.title
        )
        return {"message": "Bắt đầu tạo bộ flashcard. Bạn sẽ nhận được thông báo khi hoàn tất."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put('/flashcard-sets/{flashcard_set_id}', response_model=FlashcardSetResponse, status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def update_flashcard_set(
        flashcard_set_id: int,
        flashcard_set_request: FlashcardSetRequest,
        current_user: User = Depends(get_current_user),
        service: FlashcardSetService = Depends(get_flashcard_set_service)
):
    return await service.update_flashcard_set(flashcard_set_id=flashcard_set_id,
                                              flashcard_set_request=flashcard_set_request,
                                              user_id=current_user.id)


@router.delete('/flashcard-sets/{flashcard_set_id}', status_code=status.HTTP_204_NO_CONTENT)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def delete_flashcard_set(
        flashcard_set_id: int,
        current_user: User = Depends(get_current_user),
        service: FlashcardSetService = Depends(get_flashcard_set_service)
):
    return await service.delete_flashcard_set(flashcard_set_id=flashcard_set_id, user_id=current_user.id)
