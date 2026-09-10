import os
import json
import time
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.chat_session import ChatSession
from app.rag.generate.answer_generator import stream_answer

TEST_QUESTIONS = [
    "Đặc điểm của ngôn ngữ Java là gì?",
    "Ưu điểm và nhược điểm của Lập trình tuyến tính là gì?",
    "Cho ví dụ code minh họa cho phần Nhập xuất console?",
    "Biến là gì?",
    "So sánh overriding và overloading"
]

async def test_rag_speed():
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.is_active == True))).scalars().first()
        if not user:
            return

        chat_session = ChatSession(title="Test Latency Local", user_id=user.id)
        session.add(chat_session)
        await session.commit()
        
        print("Đang khởi động (warm-up) các model và kết nối. Vui lòng đợi...")
        try:
            async for _ in stream_answer("Xin chào, đây là câu hỏi warmup", chat_session.id, session):
                pass
        except Exception:
            pass
        print("\nKhởi động xong! Bắt đầu đo thời gian thực tế...\n")

        results = []

        for q in TEST_QUESTIONS:
            start_time = time.perf_counter()
            ttft = None
            
            try:
                async for chunk in stream_answer(q, chat_session.id, session):
                    if ttft is None and chunk:
                        ttft = time.perf_counter() - start_time
            except Exception:
                pass

            total_time = time.perf_counter() - start_time
            ttft = ttft or total_time
            
            results.append({
                "question": q,
                "ttft": round(ttft, 4),
                "total_time": round(total_time, 4),
            })
            
            await asyncio.sleep(1)

        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"latency_report.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(test_rag_speed())
