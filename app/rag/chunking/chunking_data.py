import json
import re
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def group_blocks_from_memory(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    grouped_sections = {}

    for block in records:
        if block['block_type'] == 'heading':
            continue

        # NOI HEADING_PATH
        path_key = " > ".join(block['heading_path']) if block.get('heading_path') else "General"

        if path_key not in grouped_sections:
            grouped_sections[path_key] = {
                "text": "",
                "metadata": {
                    "source": block['source_file'],
                    "topic_path": path_key,
                    "start_page": block['page_number']
                }
            }

        block_text = block['text']

        block_text = re.sub(r'(^|\n)đ (error|warning)', r'\1-> \2', block_text)

        # CHUYEN THANH MARKDOWN NEU LA CODE
        if block.get('block_type') == 'code':
            block_text = f"```cpp\n{block_text}\n```"

        # NOI NOI DUNG VAO CHU DE TUONG UNG
        grouped_sections[path_key]["text"] += block_text + "\n\n"

    return grouped_sections


def create_langchain_documents(grouped_sections: Dict[str, Any]) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    documents = []
    for path_key, data in grouped_sections.items():
        if not data["text"].strip():
            continue

        doc = Document(page_content=data["text"].strip(), metadata=data["metadata"])
        splits = text_splitter.split_documents([doc])
        documents.extend(splits)

    return documents

#
# def save_chunks_to_jsonl(chunks: List[Document], output_path: Path):
#     output_path.parent.mkdir(parents=True, exist_ok=True)
#     with open(output_path, 'w', encoding='utf-8') as f:
#         for chunk in chunks:
#             chunk_dict = {
#                 "page_content": chunk.page_content,
#                 "metadata": chunk.metadata
#             }
#             f.write(json.dumps(chunk_dict, ensure_ascii=False) + "\n")