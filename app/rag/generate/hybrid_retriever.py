from langchain_classic.retrievers import ContextualCompressionRetriever, EnsembleRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from app.rag.model import rag_models_instance

def get_hybrid_reranked_retriever(top_k: int = 3):
    vectorstore = rag_models_instance.vectorstore
    print("Công thức tính độ tương đồng của Chroma:", vectorstore._collection.metadata)
    chroma_retriever = vectorstore.as_retriever(search_kwargs={"k": top_k * 2})

    bm25_retriever = rag_models_instance.bm25_retriever
    if bm25_retriever is not None:
        bm25_retriever.k = top_k * 3
        base_retriever = EnsembleRetriever(retrievers=[bm25_retriever, chroma_retriever], weights=[0.5, 0.5])
    else:
        base_retriever = chroma_retriever

    cross_encoder = rag_models_instance.cross_encoder
    compressor = CrossEncoderReranker(model=cross_encoder, top_n=top_k)
    compression_retriever = ContextualCompressionRetriever(base_compressor=compressor,base_retriever=base_retriever)

    return compression_retriever