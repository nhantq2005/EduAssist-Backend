import json
import asyncio
import time
from app.rag.generate.hybrid_retriever import get_hybrid_reranked_retriever

async def evaluate_retrieval():
    try:
        with open("data/test_dataset.json", "r", encoding="utf-8") as f:
            dataset = json.load(f)
    except Exception as e:
        print(f"Lỗi tải dataset: {e}")
        return

    print(f"{len(dataset)} test cases.")
    retriever = get_hybrid_reranked_retriever(top_k=5)
    top_1_correct = 0
    top_3_correct = 0
    top_5_correct = 0
    mrr_sum = 0.0

    failed_cases = []
    source_error_counts = {}

    print("\nBẮT ĐẦU")
    start_time = time.time()
    for i, item in enumerate(dataset):
        query = item["question"]
        expected_source = item["expected_source"]
        expected_page = item["expected_page"]

        try:
            docs = await asyncio.to_thread(retriever.invoke, query)
        except Exception as e:
            print(f"{query}: {e}")
            continue

        found_at_rank = -1
        retrieved_info = []

        for rank, doc in enumerate(docs):
            doc_source = str(doc.metadata.get("source", ""))
            doc_filename = doc_source.split("/")[-1].split("\\")[-1]
            doc_page = doc.metadata.get("start_page")

            retrieved_info.append({
                "rank": rank + 1,
                "source": doc_filename,
                "page": doc_page
            })

            if expected_source in doc_source and doc_page == expected_page:
                found_at_rank = rank + 1
                break

        if found_at_rank == 1:
            top_1_correct += 1
        if found_at_rank > 0 and found_at_rank <= 3:
            top_3_correct += 1
        if found_at_rank > 0 and found_at_rank <= 5:
            top_5_correct += 1

        if found_at_rank == -1:
            failed_cases.append({
                "id": item.get("id", i + 1),
                "question": query,
                "expected": f"{expected_source} (Page {expected_page})",
                "retrieved_top_5": retrieved_info
            })
            source_error_counts[expected_source] = source_error_counts.get(expected_source, 0) + 1

        if found_at_rank > 0:
            mrr_sum += 1.0 / found_at_rank

        if (i + 1) % 10 == 0:
            print(f"{i + 1}/{len(dataset)}")

    end_time = time.time()
    total = len(dataset)

    report_data = {
        "result": {
            "total_test_cases": total,
            "failed_cases_count": len(failed_cases),
            "top_1_accuracy": f"{top_1_correct / total * 100:.2f}%",
            "top_3_accuracy": f"{top_3_correct / total * 100:.2f}%",
            "top_5_accuracy": f"{top_5_correct / total * 100:.2f}%",
            "MRR": f"{mrr_sum / total:.4f}",
            "Thời gian truy xuất": f"{end_time - start_time:.2f} giây"
        },
        "failed_details": failed_cases
    }

    with open("results/retrieval_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    # print("\n" + "="*40)
    # print("KẾT QUẢ TRUY XUẤT")
    # print("="*40)
    # print(f"Test cases : {total}")
    # print(f"Top-1 Accuracy   : {top_1_correct / total * 100:.2f}% ({top_1_correct}/{total})")
    # print(f"Top-3 Accuracy   : {top_3_correct / total * 100:.2f}% ({top_3_correct}/{total})")
    # print(f"Top-5 Accuracy   : {top_5_correct / total * 100:.2f}% ({top_5_correct}/{total})")
    # print(f"MRR              : {mrr_sum / total:.4f}")
    # print(f"Time taken       : {end_time - start_time:.2f} seconds")
    # print("="*40)


if __name__ == "__main__":
    asyncio.run(evaluate_retrieval())
