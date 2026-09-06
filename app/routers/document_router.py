from datetime import date
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from app.api.dependencies import get_current_user, get_document_service
from app.core.permissions import require_role
from app.models import User
from app.schemas.document import DocumentRequest, DocumentResponse, DocumentUpdateRequest
from app.services.document_service import DocumentService

router = APIRouter(tags=["documents"])


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
@require_role(["ADMIN", "LECTURER"])
async def create_document(
        background_tasks: BackgroundTasks,
        title: str = Form(...),
        subject_id: int = Form(...),
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        document_service: DocumentService = Depends(get_document_service)
):
    document_request = DocumentRequest(
        title=title,
        lecturer_id=current_user.id,
        subject_id=subject_id
    )
    document = await document_service.create_document(
        document_request=document_request,
        file=file,
        background_tasks=background_tasks
    )

    return document


@router.get("/subjects/{subject_id}/documents", response_model=list[DocumentResponse], status_code=status.HTTP_200_OK)
async def get_documents_by_subject(
        subject_id: int,
        limit: int | None = None,
        offset: int | None = None,
        document_service: DocumentService = Depends(get_document_service)
):
    params = {
        "limit": limit,
        "offset": offset,
    }
    documents = await document_service.get_documents_by_subject_id(subject_id=subject_id, params=params)
    return documents


@router.get("/documents", response_model=list[DocumentResponse], status_code=status.HTTP_200_OK)
async def get_all_documents(
        title: str | None = None,
        created_date: date | None = None,
        limit: int | None = None,
        offset: int | None = None,
        document_service: DocumentService = Depends(get_document_service)
):
    params = {
        "title": title,
        "created_date": created_date,
        "limit": limit,
        "offset": offset,
    }
    return await document_service.get_all_documents(params=params)


@router.get("/documents/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
async def get_document_by_id(
        document_id: int,
        document_service: DocumentService = Depends(get_document_service)
):
    document = await document_service.get_document_by_id(document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")
    return document


@router.put("/documents/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
@require_role(["ADMIN", "LECTURER"])
async def update_document(
        document_id: int,
        background_tasks: BackgroundTasks,
        title: str | None = Form(None),
        subject_id: int | None = Form(None),
        file: UploadFile | None = File(None),
        current_user: User = Depends(get_current_user),
        document_service: DocumentService = Depends(get_document_service),
):
    document_request = DocumentUpdateRequest(
        title=title,
        lecturer_id=current_user.id,
        subject_id=subject_id,
    )
    document = await document_service.update_document(
        document_id=document_id,
        document_request=document_request,
        file=file,
        background_tasks=background_tasks
    )
    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu để cập nhật")
    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role(["ADMIN", "LECTURER"])
async def delete_document(
        document_id: int,
        background_tasks: BackgroundTasks,
        current_user: User = Depends(get_current_user),
        document_service: DocumentService = Depends(get_document_service)
):
    document = await document_service.delete_document(document_id=document_id, background_tasks=background_tasks)
    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu để xóa")
