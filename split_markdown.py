import os
import re
import uuid
import json
from typing import List, Dict

CHINESE_NUM = "〇一二三四五六七八九十百千萬零壹貳參肆伍陸柒捌玖拾"
STRUCTURED_TITLE_REGEX = re.compile(r"(第[" + CHINESE_NUM + r"\d]{1,10}[章节讲回篇])")

def detect_structured_headings(text: str) -> List[re.Match]:
    return list(STRUCTURED_TITLE_REGEX.finditer(text))

def split_by_structure(text: str) -> List[Dict]:
    matches = detect_structured_headings(text)
    chunks = []
    if not matches:
        return []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()
        chapter_title = matches[i].group()
        chunks.append({
            "chapter_title": chapter_title,
            "content": section_text
        })
    return chunks

def semantic_fallback_split(text: str, max_len=400) -> List[str]:
    sentences = re.split(r"(?<=[。！？])", text)
    buffer = ""
    results = []
    for s in sentences:
        if len(buffer) + len(s) > max_len:
            results.append(buffer.strip())
            buffer = s
        else:
            buffer += s
    if buffer:
        results.append(buffer.strip())
    return results

def process_md_to_json(md_path: str, output_json_path: str) -> str:
    with open(md_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    structured_chunks = split_by_structure(full_text)
    output_chunks = []

    if structured_chunks:
        for chunk in structured_chunks:
            sub_chunks = semantic_fallback_split(chunk["content"])
            for sub in sub_chunks:
                output_chunks.append({
                    "id": str(uuid.uuid4()),
                    "title": os.path.basename(md_path),
                    "chapter_title": chunk["chapter_title"],
                    "content": sub,
                    "language": "zh",
                    "source_file": os.path.basename(md_path),
                    "source_type": "markdown"
                })
    else:
        fallback_chunks = semantic_fallback_split(full_text)
        for sub in fallback_chunks:
            output_chunks.append({
                "id": str(uuid.uuid4()),
                "title": os.path.basename(md_path),
                "chapter_title": None,
                "content": sub,
                "language": "zh",
                "source_file": os.path.basename(md_path),
                "source_type": "markdown"
            })

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(output_chunks, f, ensure_ascii=False, indent=2)

    print(f"✅ 成功生成 JSON 文件: {output_json_path}")
    return output_json_path

## 主程序
if __name__ == "__main__":
    input_dir = "/Users/liqingyun/Documents/Dao_AI/Dao_AI/book_markdown"
    output_dir = "/Users/liqingyun/Documents/Dao_AI/Dao_AI/book_split"

    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith(".md"):
            input_path = os.path.join(input_dir, file_name)
            output_path = os.path.join(output_dir, os.path.splitext(file_name)[0] + ".json")
            print(f"📖 处理中：{file_name}")
            try:
                process_md_to_json(input_path, output_path)
            except Exception as e:
                print(f"⚠️ 处理失败：{file_name}, 错误：{e}")