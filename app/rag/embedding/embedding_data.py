from app.core.config import settings
from langchain_core.documents import Document
from app.rag.model import rag_models_instance


def embed_and_save_to_chroma(documents: list[Document], collection_name: str = "data-collection"):
    chroma_db_dir = settings.CHROMA_DB_DIR

    if not documents:
        print("Document không có dữ liệu")
        return
    embeddings = rag_models_instance.embeddings
    print(f"Đang thêm {len(documents)} chunks mới vào ChromaDB")
    vectorstore = rag_models_instance.vectorstore
    vectorstore.add_documents(documents)

    print(f"Lưu thành công vào ChromaDB tại: {chroma_db_dir}")
    return vectorstore