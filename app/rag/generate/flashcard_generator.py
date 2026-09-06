from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.flashcard import Flashcard
from app.models.flashcard_set import FlashcardSet
from pydantic import BaseModel, Field
from app.models.document import Document
from app.rag.model import rag_models_instance
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio
import random

from app.schemas.flashcard import FlashcardList


async def generate_from_chromadb(db: AsyncSession, document_id: int, user_id: int, title: str) -> FlashcardSet:
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    
    if not doc or not doc.file_name:
        raise ValueError("Document không tồn tại hoặc không có tên file")

    vectorstore = rag_models_instance.vectorstore
    chroma_results = await asyncio.to_thread(vectorstore.get, where={"source": doc.file_name})
    chunks = chroma_results.get("documents") or []

    if not chunks:
        raise ValueError("Không tìm thấy dữ liệu text của tài liệu này trong ChromaDB.")

    merged_texts = []
    current_text = ""
    for chunk_text in chunks:
        current_text += chunk_text + "\n\n"
        if len(current_text) > 1500:
            merged_texts.append(current_text)
            current_text = ""
    if current_text:
        merged_texts.append(current_text)

    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.3)
    structured_llm = llm.with_structured_output(FlashcardList)
    sem = asyncio.Semaphore(5)

    async def process_block(text_block):
        prompt = f"""
            Bạn là trợ lý giảng dạy. Đọc nội dung bài học sau và tạo ra các flashcard (câu hỏi - đáp án)
            để ôn tập. Chỉ tập trung vào những định nghĩa, thuật ngữ và ý chính.

            Nội dung:
            {text_block}
        """
        async with sem:
            try:
                return await structured_llm.ainvoke(prompt)
            except Exception as e:
                print(f"Lỗi gọi LLM ở đoạn text này, bỏ qua: {e}")
                return None

    sampled_texts = random.sample(merged_texts, min(10, len(merged_texts)))

    tasks = [process_block(block) for block in sampled_texts]
    results = await asyncio.gather(*tasks)

    all_extracted_cards = []
    for cards_result in results:
        if cards_result and cards_result.flashcards:
            all_extracted_cards.extend(cards_result.flashcards)
            
    if not all_extracted_cards:
        raise ValueError("Không thể tạo được flashcard nào từ tài liệu này (có thể do lỗi kết nối với Gemini).")

    new_set = FlashcardSet(title=title, document_id=document_id, user_id=user_id)
    db.add(new_set)
    await db.flush()

    for card_data in all_extracted_cards:
        flashcard = Flashcard(
            front=card_data.front,
            back=card_data.back,
            flashcard_set_id=new_set.id
        )
        db.add(flashcard)

    await db.commit()
    await db.refresh(new_set)
    return new_set
