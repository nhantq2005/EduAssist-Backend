from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# 1. Load Tokenizer và Model trực tiếp thay vì dùng pipeline
tokenizer = AutoTokenizer.from_pretrained("bmd1905/vietnamese-correction")
model = AutoModelForSeq2SeqLM.from_pretrained("bmd1905/vietnamese-correction")


def correct_vietnamese_offline(query: str) -> str:
    # 2. Tokenize câu hỏi
    inputs = tokenizer(query, return_tensors="pt")

    # 3. Chạy model để dự đoán (generate) câu đã sửa
    outputs = model.generate(**inputs, max_length=128)

    # 4. Giải mã kết quả về lại text
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result

    # Test thử


if __name__ == "__main__":
    test_query = "hom nay thoi tiet the nao"
    print("Câu gốc:", test_query)
    print("Đã sửa:", correct_vietnamese_offline(test_query))