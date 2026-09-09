from app.rag.chunking.chunking_data import create_langchain_documents, group_blocks_from_memory
from app.rag.embedding.bm25_index import update_bm25_index
from app.rag.embedding.embedding_data import embed_and_save_to_chroma
from app.rag.preprocessing.read_pdf import extract_pdf
import asyncio

def run_pipeline_sync(file_bytes: bytes, file_name: str):
    records = extract_pdf(file_bytes, file_name)
    grouped_data = group_blocks_from_memory(records)
    final_chunks = create_langchain_documents(grouped_data)
    embed_and_save_to_chroma(final_chunks, collection_name="data_collection")
    update_bm25_index(final_chunks)

async def process_document_pipeline(document_id: int, file_bytes: bytes, file_name: str, session):
    try:
        await asyncio.to_thread(run_pipeline_sync, file_bytes, file_name)
    except Exception as e:
        print(f"Lỗi xử lý: {document_id}: {e!s}")