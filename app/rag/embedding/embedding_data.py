from pathlib import Path
from typing import List

import torch
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


def embed_and_save_to_chroma(documents: List[Document], collection_name: str = "data-collection"):
    CURRENT_FILE = Path(__file__).resolve()
    ROOT_DIR = CURRENT_FILE.parents[3] if len(CURRENT_FILE.parents) > 3 else CURRENT_FILE.parent
    chroma_db_dir = ROOT_DIR / "chroma_db"

    if not documents:
        print("Document không có dữ liệu")
        return

    model_name = "BAAI/bge-m3"
    print(f"EMBEDDING MODEL: {model_name}")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # KHOI TAO MODEL EMBEDDING
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': device},
        encode_kwargs={'normalize_embeddings': True}
    )

    print(f"Đang thêm {len(documents)} chunks mới vào ChromaDB")

    # KHOI TAO CHROMADB
    vectorstore = Chroma(
        persist_directory=str(chroma_db_dir),
        embedding_function=embeddings,
        collection_name=collection_name
    )
    vectorstore.add_documents(documents)

    print(f"Lưu thành công vào ChromaDB tại: {chroma_db_dir}")
    return vectorstore