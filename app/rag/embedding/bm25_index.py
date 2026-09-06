import pickle
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from app.core.config import settings


def update_bm25_index(new_documents: list[Document]):
    existing_docs = []
    if settings.BM25_SAVE_PATH.exists():
        with open(settings.BM25_SAVE_PATH, 'rb') as f:
            old_retriever = pickle.load(f)
            existing_docs = old_retriever.docs
    all_docs = existing_docs + new_documents
    updated_retriever = BM25Retriever.from_documents(all_docs)
    with open(settings.BM25_SAVE_PATH, 'wb') as f:
        pickle.dump(updated_retriever, f)

    print(f"Đã cập nhật thành công BM25 Index ({len(all_docs)} chunks)!")