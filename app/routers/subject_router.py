from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_subject_service
from app.core.permissions import require_role
from app.schemas.subject import SubjectRequest, SubjectResponse, SubjectDetailRespone
from app.services.subject_service import SubjectService

router = APIRouter(tags=["Subjects"])


@router.post("/subjects", response_model=SubjectResponse)
@require_role(["ADMIN"])
async def create_subject(subject: SubjectRequest, subject_service: SubjectService = Depends(get_subject_service)):
    return await subject_service.create_subject(subject=subject)


@router.get("/subjects", response_model=List[SubjectResponse])
async def get_subjects(
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        name: Optional[str] = None,
        subject_service: SubjectService = Depends(get_subject_service)
):
    params = {
        "offset": offset,
        "limit": limit,
        "name": name
    }
    return await subject_service.get_subjects(params)


@router.get("/subjects/{subject_id}", response_model=SubjectDetailRespone)
async def get_subject(subject_id: int, subject_service: SubjectService = Depends(get_subject_service)):
    db_subject = await subject_service.get_subject_by_id(subject_id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_subject


@router.put("/subjects/{subject_id}", response_model=SubjectResponse)
@require_role(["ADMIN", "LECTURE"])
async def update_subject(subject_id: int, subject: SubjectRequest,
                         subject_service: SubjectService = Depends(get_subject_service)):
    db_subject = await subject_service.update_subject(subject_id=subject_id, subject=subject)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_subject


@router.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role(["ADMIN", "LECTURE"])
async def delete_subject(
        subject_id: int,
        subject_service: SubjectService = Depends(get_subject_service)
):
    success = await subject_service.delete_subject(subject_id=subject_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy môn học"
        )
    return None


@router.get("/users/{lecture_id}/subjects", response_model=SubjectResponse)
async def get_subjects_by_lecture(
        lecture_id: int,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        name: Optional[str] = None,
        subject_service: SubjectService = Depends(get_subject_service)
):
    params = {
        "offset": offset,
        "limit": limit,
        "name": name
    }
    subjects = subject_service.get_subjects_by_lecturer(lecture_id, params)
    if subjects is None:
        raise HTTPException(status_code=404, detail="Không tim thấy giảng viên")
    return subjects
