import pickle
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

def update_bm25_index(new_documents: list[Document]):
    CURRENT_FILE = Path(__file__).resolve()
    ROOT_DIR = CURRENT_FILE.parents[3] if len(CURRENT_FILE.parents) > 3 else CURRENT_FILE.parent
    bm25_save_path = ROOT_DIR / "bm25_index.pkl"

    existing_docs = []
    if bm25_save_path.exists():
        with open(bm25_save_path, 'rb') as f:
            old_retriever = pickle.load(f)
            existing_docs = old_retriever.docs
    all_docs = existing_docs + new_documents
    updated_retriever = BM25Retriever.from_documents(all_docs)
    with open(bm25_save_path, 'wb') as f:
        pickle.dump(updated_retriever, f)

    print(f"Đã cập nhật thành công BM25 Index ({len(all_docs)} chunks)!")