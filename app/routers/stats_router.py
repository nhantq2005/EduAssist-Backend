from typing import List

from fastapi import APIRouter, Depends
from app.api.dependencies import get_stats_service
from app.schemas.stats import DocumentCountBySubjectResponse
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/count-docs-by-lecture/{lecture_id}", response_model=int)
async def count_document_by_lecture(lecture_id: int, stats_service: StatsService = Depends(get_stats_service)):
    return await stats_service.count_document_by_lecture(lecture_id=lecture_id)


@router.get("/count-subjects-by-lecture/{lecture_id}", response_model=int)
async def count_subject_by_lecture(lecture_id: int, stats_service: StatsService = Depends(get_stats_service)):
    return await stats_service.count_subject_by_lecture(lecture_id=lecture_id)


@router.get("/count-quizzes-by-subject/{subject_id}", response_model=int)
async def count_quiz_by_subject(subject_id: int, stats_service: StatsService = Depends(get_stats_service)):
    return await stats_service.count_quiz_by_subject(subject_id=subject_id)


@router.get("/count-lectures", response_model=int)
async def count_lectures(stats_service: StatsService = Depends(get_stats_service)):
    return await stats_service.count_lecture()


@router.get("/count-students", response_model=int)
async def count_students(stats_service: StatsService = Depends(get_stats_service)):
    return await stats_service.count_student()


@router.get("/stats-docs-by-subject", response_model=List[DocumentCountBySubjectResponse])
async def count_documents_by_subject(stats_service: StatsService = Depends(get_stats_service)):
    return await stats_service.count_documents_by_subject()
