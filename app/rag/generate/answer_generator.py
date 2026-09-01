# from app.models.chat_session import ChatSession
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import PromptTemplate
# from langchain_core.runnables import RunnablePassthrough
# from langchain_core.output_parsers import StrOutputParser
# from dotenv import load_dotenv
# from app.rag.generate.hybrid_retriever import get_hybrid_reranked_retriever
# from app.services import chat_message_service
# from app.schemas.chat_message import ChatMessageCreate
# from sqlalchemy.ext.asyncio import AsyncSession
#
# load_dotenv()
#
#
# def format_docs(docs):
#     formatted_str = ""
#     for i, doc in enumerate(docs):
#         # LAY METADATA DE BIET NGUON GOC
#         source = doc.metadata.get("source", "Không rõ")
#         page = doc.metadata.get("start_page", "Không rõ")
#         topic = doc.metadata.get("topic_path", "Không rõ")
#
#         formatted_str += f"[Tài liệu {i + 1} | Nguồn: {source} | Trang: {page} | Chủ đề: {topic}]\n{doc.page_content}\n\n"
#     return formatted_str
#
#
# def get_rag_chain():
#     retriever = get_hybrid_reranked_retriever(top_k=3)
#     llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.2)
#
#     template = """Bạn là một Trợ giảng AI chuyên ngành Công nghệ thông tin.
#                 Nhiệm vụ của bạn là giải đáp thắc mắc của sinh viên một cách chi tiết, dễ hiểu, mang tính sư phạm và khơi gợi tư duy.
#
#                 HÃY TUÂN THỦ NGHIÊM NGẶT CÁC QUY TẮC SAU:
#                 1. Dựa TRỰC TIẾP vào các đoạn tài liệu (Context) được cung cấp bên dưới để trả lời.
#                 2. Nếu Context KHÔNG chứa thông tin để trả lời, hãy nói: "Xin lỗi, hiện tại tài liệu môn học chưa đề cập đến vấn đề này, bạn có thể làm rõ hơn câu hỏi được không?". TUYỆT ĐỐI KHÔNG tự bịa ra thông tin không có trong Context.
#                 3. Nếu Context chỉ chứa một phần câu trả lời, hãy giải đáp phần đó và nói rõ tài liệu chưa cung cấp đủ thông tin cho phần còn lại.
#                 4. Luôn định dạng code (nếu có) bằng Markdown rõ ràng.
#                 5. Cuối mỗi ý hoặc câu trả lời, PHẢI trích dẫn nguồn theo định dạng: [Tên tài liệu - Trang X] để sinh viên tiện tra cứu.
#
#                 NGỮ CẢNH (CONTEXT):
#                 {context}
#
#                 CÂU HỎI CỦA SINH VIÊN:
#                 {question}
#
#                 CÂU TRẢ LỜI CỦA TRỢ GIẢNG:
#                 """
#
#     prompt = PromptTemplate.from_template(template)
#
#     # XAU CHUOI QUY TRINH (LangChain LCEL)
#     rag_chain = (
#             {"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
#     )
#
#     return rag_chain
#
#
# async def stream_answer(query: str, chat_session_id: int, db: AsyncSession):
#     rag_chain = get_rag_chain()
#
#     full_answer = ""
#     async for chunk in rag_chain.astream(query):
#         full_answer += chunk
#         yield chunk
#     # LUU VAO BANG CHAT_MESSAGE
#     chat_message_svc = chat_message_service.ChatMessageService(db)
#
#     # LAY MESSAGE DAU TIEN LAM TIEU DE CHO CHAT_SESSION
#     chat_session = await db.get(ChatSession, chat_session_id)
#     if chat_session and chat_session.title == "Đoạn chat mới":
#         chat_session.title = query[:30] + ("..." if len(query) > 30 else "")
#         db.add(chat_session)
#         await db.commit()
#
#     chat_message_create = ChatMessageCreate(
#         question=query,
#         answer=full_answer,
#         chat_session_id=chat_session_id
#     )
#     print(full_answer)
#     await chat_message_svc.create_chat_message(chat_message_create)
#


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

MAX_HISTORY_TURNS = 3


def format_chat_history(messages):
    if not messages:
        return "Chưa có lịch sử hội thoại."

    recent_messages = messages[-MAX_HISTORY_TURNS:]

    history_str = ""
    for msg in recent_messages:
        history_str += f"Sinh viên: {msg.question}\n"
        history_str += f"Trợ giảng: {msg.answer}\n\n"
    return history_str.strip()


def format_docs(docs):
    formatted_str = ""
    for i, doc in enumerate(docs):
        # LAY METADATA DE BIET NGUON GOC
        source = doc.metadata.get("source", "Không rõ")
        page = doc.metadata.get("start_page", "Không rõ")
        topic = doc.metadata.get("topic_path", "Không rõ")

        formatted_str += f"[Tài liệu {i + 1} | Nguồn: {source} | Trang: {page} | Chủ đề: {topic}]\n{doc.page_content}\n\n"
    return formatted_str


def get_rag_chain():
    retriever = get_hybrid_reranked_retriever(top_k=3)
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.2)

    template = """Bạn là một Trợ giảng AI chuyên ngành Công nghệ thông tin. 
                Nhiệm vụ của bạn là giải đáp thắc mắc của sinh viên một cách chi tiết, dễ hiểu, mang tính sư phạm và khơi gợi tư duy.

                HÃY TUÂN THỦ NGHIÊM NGẶT CÁC QUY TẮC SAU:
                1. Dựa TRỰC TIẾP vào các đoạn tài liệu (Context) được cung cấp bên dưới để trả lời.
                2. Nếu Context KHÔNG chứa thông tin để trả lời, hãy nói: "Xin lỗi, hiện tại tài liệu môn học chưa đề cập đến vấn đề này, bạn có thể làm rõ hơn câu hỏi được không?". TUYỆT ĐỐI KHÔNG tự bịa ra thông tin không có trong Context.
                3. Nếu Context chỉ chứa một phần câu trả lời, hãy giải đáp phần đó và nói rõ tài liệu chưa cung cấp đủ thông tin cho phần còn lại.
                4. Luôn định dạng code (nếu có) bằng Markdown rõ ràng.
                5. Cuối mỗi ý hoặc câu trả lời, PHẢI trích dẫn nguồn theo định dạng: [Tên tài liệu - Trang X] để sinh viên tiện tra cứu.
                6. Sử dụng LỊCH SỬ HỘI THOẠI bên dưới để hiểu ngữ cảnh câu hỏi (ví dụ: "nó", "cái đó", "giải thích thêm" đang nói về gì). Nhưng vẫn ưu tiên trả lời dựa trên Context tài liệu.

                LỊCH SỬ HỘI THOẠI TRƯỚC ĐÓ:
                {chat_history}

                NGỮ CẢNH (CONTEXT):
                {context}

                CÂU HỎI CỦA SINH VIÊN:
                {question}

                CÂU TRẢ LỜI CỦA TRỢ GIẢNG:
                """

    prompt = PromptTemplate.from_template(template)

    # XAU CHUOI QUY TRINH (LangChain LCEL)
    rag_chain = (
            prompt | llm | StrOutputParser()
    )

    return rag_chain, retriever


async def stream_answer(query: str, chat_session_id: int, db: AsyncSession):
    rag_chain, retriever = get_rag_chain()

    chat_message_svc = chat_message_service.ChatMessageService(db)
    history_messages = await chat_message_svc.get_message_in_session(chat_session_id)
    chat_history_text = format_chat_history(history_messages)

    docs = await asyncio.to_thread(retriever.invoke, query)
    context_text = format_docs(docs)

    full_answer = ""
    async for chunk in rag_chain.astream({
        "chat_history": chat_history_text,
        "context": context_text,
        "question": query
    }):
        full_answer += chunk
        yield chunk

    # LUU VAO BANG CHAT_MESSAGE
    # LAY MESSAGE DAU TIEN LAM TIEU DE CHO CHAT_SESSION
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
