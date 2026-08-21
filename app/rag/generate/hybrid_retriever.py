from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_classic.retrievers import EnsembleRetriever
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from app.rag.model import rag_models_instance

def get_hybrid_reranked_retriever(top_k: int = 3):
    CURRENT_FILE = Path(__file__).resolve()
    ROOT_DIR = CURRENT_FILE.parents[3] if len(CURRENT_FILE.parents) > 3 else CURRENT_FILE.parent
    chroma_db_dir = ROOT_DIR / "chroma_db"

    # LAY EMBEDDING TỪ SINGLETON
    embeddings = rag_models_instance.embeddings
    
    vectorstore = Chroma(
        persist_directory=str(chroma_db_dir),
        embedding_function=embeddings,
        collection_name="cslt_collection"
    )
    print("Công thức tính độ tương đồng của Chroma:", vectorstore._collection.metadata)
    # LAY KET QUA (LAY GAP 2)
    chroma_retriever = vectorstore.as_retriever(search_kwargs={"k": top_k * 2})

    # LAY BM25 TỪ SINGLETON
    bm25_retriever = rag_models_instance.bm25_retriever
    bm25_retriever.k = top_k * 2

    # ENSEMBLE RETRIEVER (50/50)
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, chroma_retriever],
        weights=[0.5, 0.5]
    )

    # LAY RE-RANKER TỪ SINGLETON
    cross_encoder = rag_models_instance.cross_encoder

    # Cấu hình bộ nén: Chấm điểm và chỉ giữ lại số lượng tài liệu đúng bằng top_k
    compressor = CrossEncoderReranker(model=cross_encoder, top_n=top_k)

    # Bọc bộ tìm kiếm tổng hợp qua lớp Nén (Compression)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=ensemble_retriever
    )

    return compression_retriever