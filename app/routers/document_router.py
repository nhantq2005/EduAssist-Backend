from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from app.api.dependencies import get_document_service, get_current_user
from app.core.permissions import require_role
from app.models import User
from app.schemas.document import DocumentRequest, DocumentResponse, DocumentUpdateRequest
from fastapi import UploadFile, File, BackgroundTasks
from app.services.document_service import DocumentService
from app.rag.processing_pipeline import process_document_pipeline
from app.db.session import AsyncSessionLocal


async def run_pipeline_task(document_id: int, file_bytes: bytes, file_name: str):
    async with AsyncSessionLocal() as session:
        await process_document_pipeline(document_id, file_bytes, file_name, session)


router = APIRouter(tags=["documents"])


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
@require_role(["ADMIN", "LECTURE"])
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
        subject_id=subject_id,
    )
    document = await document_service.create_document(document_request=document_request, file=file)
    await file.seek(0)
    file_bytes = await file.read()
    background_tasks.add_task(run_pipeline_task, document.id, file_bytes, file.filename)
    return document


@router.get("/subjects/{subject_id}/documents", response_model=List[DocumentResponse])
async def get_documents_by_subject(
        subject_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        document_service: DocumentService = Depends(get_document_service)
):
    params = {
        "limit": limit,
        "offset": offset,
    }
    documents = await document_service.get_documents_by_subject_id(subject_id, params)
    return documents


@router.get("/documents", response_model=List[DocumentResponse])
async def get_all_documents(
        title: Optional[str] = None,
        created_date: Optional[date] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        document_service: DocumentService = Depends(get_document_service)
):
    params = {
        "title": title,
        "created_date": created_date,
        "limit": limit,
        "offset": offset,
    }
    return await document_service.get_all_documents(params)


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document_by_id(
        document_id: int,
        document_service: DocumentService = Depends(get_document_service)
):
    document = await document_service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")
    return document


@router.put("/documents/{document_id}", response_model=DocumentResponse)
@require_role(["ADMIN", "LECTURE"])
async def update_document(
        document_id: int,
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
    document = await document_service.update_document(document_id, document_request, file)
    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu để cập nhật")
    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role(["ADMIN", "LECTURE"])
async def delete_document(
        document_id: int,
        document_service: DocumentService = Depends(get_document_service)
):
    document = await document_service.delete_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu để xóa")
    return None
