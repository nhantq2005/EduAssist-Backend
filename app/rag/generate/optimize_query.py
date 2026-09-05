# from transformers import pipeline
#
# # def diacritic_restoration_query(query):

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

print("Đang tải Tokenizer và Mô hình...")
model_name = "qthuan2604/BARTPho_Syllable_Restore_Diacritics_Vietnamese"

# 1. Khởi tạo Tokenizer và Model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


# 2. Hàm xử lý
def restore_direct(text):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=128)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

    # TEST


if __name__ == "__main__":
    cau_hoi = "api la gi va lap trinh oop kho khong?"
    print(f"Gốc    : {cau_hoi}")
    print(f"Đã sửa : {restore_direct(cau_hoi)}")