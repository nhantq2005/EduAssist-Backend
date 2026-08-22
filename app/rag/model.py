import torch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
import pickle


class RAGModels:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGModels, cls).__new__(cls)

            # cls._instance.embeddings = HuggingFaceEmbeddings(
            #     model_name="BAAI/bge-m3",
            #     model_kwargs={'device': 'cpu'},
            #     encode_kwargs={'normalize_embeddings': True}
            # )

            device_embedding = "cuda" if torch.cuda.is_available() else "cpu"
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
                    'automodel_args': {'torch_dtype': torch.float16} if device_reranker == "cuda" else {}
                }
            )

            from pathlib import Path
            import os
            CURRENT_FILE = Path(__file__).resolve()
            ROOT_DIR = CURRENT_FILE.parents[2]
            bm25_save_path = ROOT_DIR / "bm25_index.pkl"
            if os.path.exists(bm25_save_path):
                with open(bm25_save_path, 'rb') as f:
                    cls._instance.bm25_retriever = pickle.load(f)
            else:
                print(f"Không tìm thấy file {bm25_save_path}. Hãy chạy script build dữ liệu trước.")
                cls._instance.bm25_retriever = None

            from langchain_community.vectorstores import Chroma
            chroma_db_dir = ROOT_DIR / "chroma_db"
            cls._instance.vectorstore = Chroma(
                persist_directory=str(chroma_db_dir),
                embedding_function=cls._instance.embeddings,
                collection_name="cslt_collection"
            )

        print("Tải mô hình thành công")

        return cls._instance


rag_models_instance = RAGModels()
