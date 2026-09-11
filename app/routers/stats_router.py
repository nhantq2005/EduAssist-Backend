from fastapi import APIRouter, Depends, status
from app.api.dependencies import get_stats_service, get_current_user
from app.core.permissions import require_role
from app.models import User
from app.schemas.stats import DocumentCountBySubjectResponse, ScoreDistributionItem
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/count-docs-by-lecture/{lecture_id}", response_model=int, status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER"])
async def count_document_by_lecture(
        lecture_id: int,
        stats_service: StatsService = Depends(get_stats_service)
):
    return await stats_service.count_document_by_lecture(lecture_id=lecture_id)


@router.get("/count-subjects-by-lecture/{lecture_id}", response_model=int, status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER"])
async def count_subject_by_lecture(
        lecture_id: int,
        stats_service: StatsService = Depends(get_stats_service)
):
    return await stats_service.count_subject_by_lecture(lecture_id=lecture_id)


@router.get("/count-quizzes-by-subject/{subject_id}", response_model=int, status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER"])
async def count_quiz_by_subject(
        subject_id: int,
        stats_service: StatsService = Depends(get_stats_service)
):
    return await stats_service.count_quiz_by_subject(subject_id=subject_id)


@router.get("/count-lectures", response_model=int, status_code=status.HTTP_200_OK)
@require_role(["ADMIN"])
async def count_lectures(stats_service: StatsService = Depends(get_stats_service)):
    return await stats_service.count_lecture()


@router.get("/count-students", response_model=int, status_code=status.HTTP_200_OK)
@require_role(["ADMIN"])
async def count_students(stats_service: StatsService = Depends(get_stats_service)):
    return await stats_service.count_student()


@router.get("/stats-docs-by-subject", response_model=list[DocumentCountBySubjectResponse],
            status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER"])
async def count_documents_by_subject(stats_service: StatsService = Depends(get_stats_service)):
    return await stats_service.count_documents_by_subject()


@router.get("/average-score", response_model=float, status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def get_student_average_score(
        student_id: int,
        current_user: User = Depends(get_current_user),
        stats_service: StatsService = Depends(get_stats_service)
):
    return await stats_service.get_student_average_score(student_id=current_user.id)


@router.get("/score-distribution", response_model=list[ScoreDistributionItem], status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER", "STUDENT"])
async def get_score_distribution(
        current_user: User = Depends(get_current_user),
        stats_service: StatsService = Depends(get_stats_service)
):
    return await stats_service.get_score_distribution(student_id=current_user.id)
