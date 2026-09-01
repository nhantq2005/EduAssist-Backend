from pathlib import Path
from langchain_classic.retrievers import ContextualCompressionRetriever, EnsembleRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from app.rag.model import rag_models_instance

def get_hybrid_reranked_retriever(top_k: int = 3):
    CURRENT_FILE = Path(__file__).resolve()
    ROOT_DIR = CURRENT_FILE.parents[3] if len(CURRENT_FILE.parents) > 3 else CURRENT_FILE.parent
    chroma_db_dir = ROOT_DIR / "chroma_db"

    # LAY EMBEDDING TỪ SINGLETON
    embeddings = rag_models_instance.embeddings
    vectorstore = rag_models_instance.vectorstore

    print("Công thức tính độ tương đồng của Chroma:", vectorstore._collection.metadata)
    # TRUY XUAT TU CHROMA
    chroma_retriever = vectorstore.as_retriever(search_kwargs={"k": top_k * 2})

    # LAY BM25 TỪ SINGLETON
    bm25_retriever = rag_models_instance.bm25_retriever
    bm25_retriever.k = top_k * 2
    base_retriever = EnsembleRetriever(retrievers=[bm25_retriever, chroma_retriever], weights=[0.5, 0.5])

    # XEP HANG NGU CANH
    cross_encoder = rag_models_instance.cross_encoder
    compressor = CrossEncoderReranker(model=cross_encoder, top_n=top_k)
    compression_retriever = ContextualCompressionRetriever(base_compressor=compressor,base_retriever=base_retriever)

    return compression_retriever