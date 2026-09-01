from dotenv import load_dotenv
import asyncio
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from app.rag.generate.answer_generator import format_docs
from app.rag.generate.hybrid_retriever import get_hybrid_reranked_retriever
from app.schemas.quiz import QuizData
load_dotenv()




async def generate_quiz_from_topic(topic: str, num_questions: int = 5) -> QuizData:
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.3)
    # TIM DOC CO CHU DE LIEN QUAN
    retriever = get_hybrid_reranked_retriever(top_k=5)
    docs = await asyncio.to_thread(retriever.invoke, topic)
    context = format_docs(docs)
    parser = PydanticOutputParser(pydantic_object=QuizData)
    template = """Bạn là một Giảng viên đại học chuyên nghiệp. 
                Nhiệm vụ của bạn là soạn một bài kiểm tra trắc nghiệm dựa TRỰC TIẾP vào nội dung tài liệu được cung cấp dưới đây.
                
                SỐ LƯỢNG CÂU HỎI CẦN TẠO: {num_questions} câu.
                CHỦ ĐỀ: {topic}
                
                YÊU CẦU NGHIÊM NGẶT:
                1. Thông tin để làm đáp án PHẢI CÓ TRONG tài liệu. Không được tự bịa ra kiến thức bên ngoài.
                2. Mỗi câu hỏi phải có đúng 4 lựa chọn (options).
                3. Chỉ có duy nhất 1 đáp án đúng (is_correct = true), 3 đáp án còn lại là sai (is_correct = false).
                4. Phải có lời giải thích (explaination) ngắn gọn cho mỗi câu hỏi.
                5. Cung cấp kết quả ĐÚNG định dạng JSON theo cấu trúc sau:
                
                {format_instructions}
                
                TÀI LIỆU (CONTEXT):
                {context}
                """

    prompt = PromptTemplate(
        template=template,
        input_variables=["topic", "num_questions", "context"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    # XAU CHUOI KCEL
    chain = prompt | llm | parser

    try:
        quiz_data = await chain.ainvoke({
            "topic": topic,
            "num_questions": num_questions,
            "context": context
        })
        return quiz_data
    except Exception as e:
        print(f"Lỗi khi sinh trắc nghiệm: {e}")
        raise e
