import logging
import pickle
from pathlib import Path
from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from langchain_community.retrievers import BM25Retriever
from sqlalchemy import Date, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.config import settings
from app.core.websocket import manager
from app.db.session import AsyncSessionLocal
from app.models.document import Document, ProcessingStatus
from app.rag.model import rag_models_instance
from app.rag.processing_pipeline import process_document_pipeline
from app.schemas.document import DocumentRequest, DocumentUpdateRequest
from app.utils.cloudinary_utils import upload_file_to_cloudinary

ALLOWED_EXTENSIONS = {".pdf"}

logger = logging.getLogger(__name__)


async def run_pipeline_background_task(document_id: int, file_bytes: bytes, file_name: str):
    async with AsyncSessionLocal() as bg_session:
        try:
            document = await bg_session.get(Document, document_id)
            if not document:
                logger.warning(f"Không tìm thấy document ID {document_id}")
                return

            document.process_status = ProcessingStatus.PROCESSING
            await bg_session.commit()
            await process_document_pipeline(document_id, file_bytes, file_name, bg_session)

            document.process_status = ProcessingStatus.COMPLETED
            await bg_session.commit()

            await manager.broadcast({
                "type": "DOCUMENT_COMPLETED",
                "document_id": document_id,
                "message": f"Tài liệu {file_name} đã xử lý xong!"
            })
            logger.info(f"Đã xử lý xong tài liệu ID: {document_id}")

        except Exception as e:
            await manager.broadcast({
                "type": "DOCUMENT_FAILED",
                "document_id": document_id,
                "message": f"Xử lý lỗi: {file_name}"
            })
            logger.error(f"Lỗi khi xử lý tài liệu {document_id}: {e!s}")
            if 'document' in locals() and document:
                document.process_status = ProcessingStatus.FAILED
                await bg_session.commit()


def delete_document_vector_db(file_name: str):
    try:
        chroma_db_dir = settings.CHROMA_DB_DIR
        bm25_save_path = settings.BM25_SAVE_PATH
        vectorstore = rag_models_instance.vectorstore
        vectorstore._collection.delete(where={"source": file_name})
        print(f"Đã xóa toàn bộ vector của '{file_name}' khỏi ChromaDB.")
        bm25 = rag_models_instance.bm25_retriever
        if bm25 and hasattr(bm25, 'docs'):
            remaining_docs = [
                doc for doc in bm25.docs
                if doc.metadata.get("source") != file_name
            ]

            if remaining_docs:
                new_bm25 = BM25Retriever.from_documents(remaining_docs)
                rag_models_instance.bm25_retriever = new_bm25

                with open(bm25_save_path, 'wb') as f:
                    pickle.dump(new_bm25, f)
                print("Đã xóa khỏi BM25 và Build lại thành công.")
            else:
                rag_models_instance.bm25_retriever = None
                if bm25_save_path.exists():
                    bm25_save_path.unlink()
                print("CSDL rỗng, đã xóa file BM25.")

    except Exception as e:
        print(f"Xóa dữ liệu AI thất bại: {e!s}")


class DocumentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_document(
            self,
            document_request: DocumentRequest,
            file: UploadFile,
            background_tasks: BackgroundTasks
    ):
        if not file.filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên file không hợp lệ")

        extension = Path(file.filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=("Chỉ hỗ trợ định dạng PDF, Word và PowerPoint")
            )

        try:
            await file.seek(0)
            upload_result = await upload_file_to_cloudinary(file=file, folder="documents")
            file_url = upload_result.get("secure_url")

            if not file_url:
                raise RuntimeError("Cloudinary không trả về secure_url")

            document = Document(
                **document_request.model_dump(),
                file_url=file_url,
                file_type=extension.removeprefix("."),
                file_name=file.filename,
                process_status=ProcessingStatus.PENDING,
            )

            self.session.add(document)
            await self.session.commit()
            await self.session.refresh(document)

            await file.seek(0)
            file_bytes = await file.read()
            background_tasks.add_task(
                run_pipeline_background_task,
                document.id,
                file_bytes,
                file.filename
            )
            return document
        except Exception:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Không thể tạo tài liệu")

    async def get_document_by_id(self, document_id: int):
        stm = select(Document).where(Document.id == document_id)
        result = await self.session.execute(stm)
        return result.scalars().first()

    async def get_all_documents(self, params: dict):
        offset = params.get('offset', 0)
        limit = params.get('limit', 100)

        stm = select(Document)
        if params.get('title') is not None:
            stm = stm.where(Document.title.ilike(f"%{params['title']}%"))

        if params.get('created_date') is not None:
            stm = stm.where(cast(Document.created_date, Date) == params['created_date'])

        if params.get('start_date') is not None:
            stm = stm.where(cast(Document.created_date, Date) >= params['start_date'])

        if params.get('end_date') is not None:
            stm = stm.where(cast(Document.created_date, Date) <= params['end_date'])

        stm = stm.offset(offset).limit(limit)
        result = await self.session.execute(stm)
        return result.scalars().all()

    async def update_document(
            self,
            document_id: int,
            document_request: DocumentUpdateRequest,
            file: UploadFile | None = None,
            background_tasks: BackgroundTasks = None
    ):
        db_document = await self.get_document_by_id(document_id)

        if db_document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy document với id: {document_id}"
            )

        try:
            update_data = document_request.model_dump(
                exclude_unset=True,
                exclude_none=True,
            )

            for field_name, value in update_data.items():
                setattr(db_document, field_name, value)

            if file is not None:
                if not file.filename:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên file không hợp lệ")

                extension = Path(file.filename).suffix.lower()

                if extension not in ALLOWED_EXTENSIONS:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=("Chỉ hỗ trợ định dạng PDF, DOC, DOCX, PPT và PPTX")
                    )

                await file.seek(0)

                upload_result = await upload_file_to_cloudinary(
                    file=file,
                    folder="documents",
                )

                file_url = upload_result.get("secure_url")

                if not file_url:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Cloudinary không trả về secure_url",
                    )

                db_document.file_url = file_url
                db_document.file_type = extension.removeprefix(".")
                db_document.file_name = file.filename
                db_document.process_status = ProcessingStatus.PENDING

            await self.session.commit()
            await self.session.refresh(db_document)

            if file is not None and background_tasks is not None:
                await file.seek(0)
                file_bytes = await file.read()
                background_tasks.add_task(
                    run_pipeline_background_task,
                    db_document.id,
                    file_bytes,
                    file.filename
                )

            return db_document

        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể cập nhật tài liệu: {e!s}",
            )

    async def delete_document(self, document_id: int, background_tasks: BackgroundTasks = None):
        try:
            db_document = await self.get_document_by_id(document_id)
            if not db_document:
                raise Exception(f"Không tìm thấy document với id: {document_id}")
            file_name = db_document.file_name
            await self.session.delete(db_document)
            await self.session.commit()
            if background_tasks and file_name:
                background_tasks.add_task(delete_document_vector_db, file_name)
            return True
        except Exception:
            await self.session.rollback()
            raise

    async def get_documents_by_subject_id(self, subject_id: int, params: dict):
        offset = params.get('offset', 0)
        limit = params.get('limit', 100)
        stm = select(Document).where(Document.subject_id == subject_id)
        stm = stm.offset(offset).limit(limit)
        result = await self.session.execute(stm)
        return result.scalars().all()
