import pickle
import torch
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings
import os
from app.core.config import settings
from langchain_community.vectorstores import Chroma


class RAGModels:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            # device_embedding = "cuda" if torch.cuda.is_available() else "cpu"
            device_embedding =  "cpu"
            cls._instance.embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-m3",
                model_kwargs={
                    'device': device_embedding,
                },
                encode_kwargs={'normalize_embeddings': True}
            )
            print(f"EMBEDDING: {device_embedding}")

            device_reranker = "cuda" if torch.cuda.is_available() else "cpu"
            cls._instance.cross_encoder = HuggingFaceCrossEncoder(
                model_name="BAAI/bge-reranker-v2-m3",
                model_kwargs={
                    'device': device_reranker,
                    'model_kwargs': {'torch_dtype': torch.float16} if device_reranker == "cuda" else {}
                }
            )

            bm25_save_path = settings.BM25_SAVE_PATH
            if os.path.exists(bm25_save_path):
                with open(bm25_save_path, 'rb') as f:
                    cls._instance.bm25_retriever = pickle.load(f)
            else:
                print(f"Không tìm thấy file {bm25_save_path}.")
                cls._instance.bm25_retriever = None

            chroma_db_dir = settings.CHROMA_DB_DIR
            cls._instance.vectorstore = Chroma(
                persist_directory=str(chroma_db_dir),
                embedding_function=cls._instance.embeddings,
                collection_name="cslt_collection"
            )

        print("Tải mô hình thành công")
        return cls._instance


rag_models_instance = RAGModels()
