from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_user, get_subject_service
from app.core.permissions import require_role
from app.models import User
from app.schemas.subject import SubjectDetailRespone, SubjectRequest, SubjectResponse
from app.services.subject_service import SubjectService

router = APIRouter(tags=["Subjects"])


@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
@require_role(["ADMIN"])
async def create_subject(
        subject_request: SubjectRequest,
        current_user: User = Depends(get_current_user),
        subject_service: SubjectService = Depends(get_subject_service)
):
    return await subject_service.create_subject(subject_request=subject_request, lecturer_id=current_user.id)


@router.get("/subjects", response_model=list[SubjectResponse], status_code=status.HTTP_200_OK)
async def get_subjects(
        offset: int | None = 0,
        limit: int | None = 100,
        name: str | None = None,
        subject_service: SubjectService = Depends(get_subject_service)
):
    params = {
        "offset": offset,
        "limit": limit,
        "name": name
    }
    return await subject_service.get_subjects(params=params)


@router.get("/subjects/{subject_id}", response_model=SubjectDetailRespone, status_code=status.HTTP_200_OK)
async def get_subject(
        subject_id: int,
        subject_service: SubjectService = Depends(get_subject_service)
):
    db_subject = await subject_service.get_subject_by_id(subject_id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_subject


@router.put("/subjects/{subject_id}", response_model=SubjectResponse, status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER"])
async def update_subject(
        subject_id: int,
        subject_request: SubjectRequest,
        current_user: User = Depends(get_current_user),
        subject_service: SubjectService = Depends(get_subject_service)
):
    db_subject = await subject_service.update_subject(subject_id=subject_id,
                                                      subject_request=subject_request,
                                                      lecturer_id=current_user.id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
    return db_subject


@router.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role(["ADMIN", "LECTURER"])
async def delete_subject(
        subject_id: int,
        subject_service: SubjectService = Depends(get_subject_service)
):
    success = await subject_service.delete_subject(subject_id=subject_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy môn học")


@router.get("/users/{lecture_id}/subjects", response_model=list[SubjectResponse], status_code=status.HTTP_200_OK)
async def get_subjects_by_lecture(
        lecture_id: int,
        offset: int | None = 0,
        limit: int | None = 100,
        name: str | None = None,
        subject_service: SubjectService = Depends(get_subject_service)
):
    params = {
        "offset": offset,
        "limit": limit,
        "name": name
    }
    subjects = await subject_service.get_subjects_by_lecturer(lecturer_id=lecture_id, params=params)
    if subjects is None:
        raise HTTPException(status_code=404, detail="Không tim thấy giảng viên")
    return subjects
