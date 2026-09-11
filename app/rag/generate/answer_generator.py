import asyncio
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat_session import ChatSession
from app.rag.generate.hybrid_retriever import get_hybrid_reranked_retriever
from app.schemas.chat_message import ChatMessageCreate
from app.services import chat_message_service

load_dotenv()

def format_chat_history(messages):
    if not messages:
        return "Chưa có lịch sử hội thoại."
    recent_messages = messages[-3:]
    history_str = ""
    for msg in recent_messages:
        history_str += f"Sinh viên: {msg.question}\n"
        history_str += f"Trợ giảng: {msg.answer}\n\n"
    return history_str.strip()


def format_docs(docs):
    formatted_str = ""
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "?")
        page = doc.metadata.get("start_page", "?")
        topic = doc.metadata.get("topic_path", "General")
        formatted_str += f"[{source} - Trang {page} - {topic}]\n{doc.page_content}\n\n"
    return formatted_str


def get_rag_chain():
    retriever = get_hybrid_reranked_retriever(top_k=3)
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.2, thinking_level='low')
    template = """
Bạn là một Trợ giảng AI chuyên ngành Công nghệ thông tin. 
Nhiệm vụ của bạn là giải đáp thắc mắc của sinh viên một cách chi tiết, dễ hiểu, mang tính sư phạm và khơi gợi tư duy.                                                                                                                                                                                           
 QUY TẮC:
1. Trả lời dựa TRỰC TIẾP vào Context bên dưới. Có thể tổng hợp thông tin từ nhiều nguồn trong Context để tạo câu trả lời hoàn chỉnh.
2a. Nếu Context KHÔNG chứa thông tin liên quan đến câu hỏi → trả lời: "Xin lỗi, tài liệu môn học chưa đề cập đến vấn đề này." KHÔNG tự bịa kiến thức bên ngoài.
2b. Nếu Context chỉ chứa thông tin liên quan một phần → trả lời dựa trên phần đó, không suy diễn thêm, không nhắc đến việc tài liệu thiếu sót.
3. Nếu các nguồn trong Context mâu thuẫn nhau, nêu rõ sự khác biệt và trích dẫn từng nguồn tương ứng.
4. Code phải dùng Markdown code block, có chú thích ngắn gọn nếu cần.
5. Trích dẫn nguồn cuối mỗi ý: [Tên tài liệu - Trang X]. Nếu không có số trang, chỉ ghi [Tên tài liệu].
6. Luôn trả lời bằng tiếng Việt.
7. Dùng lịch sử hội thoại để hiểu ngữ cảnh câu hỏi nối tiếp.
8. Khi giải thích khái niệm: định nghĩa ngắn gọn → ví dụ minh họa (nếu có trong Context) → liên hệ/so sánh nếu phù hợp. Có thể đặt một câu hỏi gợi mở ở cuối để khuyến khích tư duy, không bắt buộc.
LỊCH SỬ HỘI THOẠI TRƯỚC ĐÓ:
{chat_history}

NGỮ CẢNH (CONTEXT):
{context}

CÂU HỎI CỦA SINH VIÊN:
{question}

CÂU TRẢ LỜI CỦA TRỢ GIẢNG:
"""
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    return chain, retriever


async def stream_answer(query: str, chat_session_id: int, db: AsyncSession):
    rag_chain, retriever = get_rag_chain()
    chat_message_svc = chat_message_service.ChatMessageService(db)
    history_messages, docs = await asyncio.gather(
        chat_message_svc.get_message_in_session(chat_session_id),
        asyncio.to_thread(retriever.invoke, query)
    )
    chat_history_text = format_chat_history(history_messages)
    context_text = format_docs(docs)
    full_answer = ""
    try:
        async for chunk in rag_chain.astream({
            "chat_history": chat_history_text,
            "context": context_text,
            "question": query
        }):
            full_answer += chunk
            yield chunk
    except Exception as e:
        error_msg = f"Lỗi kết nối với Gemini: {str(e)}"
        yield error_msg
        full_answer += error_msg

    chat_session = await db.get(ChatSession, chat_session_id)
    if chat_session and chat_session.title == "Đoạn chat mới":
        chat_session.title = query[:30] + ("..." if len(query) > 30 else "")
        db.add(chat_session)
        await db.commit()

    chat_message_create = ChatMessageCreate(
        question=query,
        answer=full_answer,
        chat_session_id=chat_session_id
    )
    print(full_answer)
    await chat_message_svc.create_chat_message(chat_message_create)
