# build_chroma.py
import os
import json
import chromadb
from tqdm import tqdm
from embedding_model import LocalEmbeddingModel

def load_chunks(json_dir):
    all_chunks = []
    for file in os.listdir(json_dir):
        if file.endswith(".json"):
            with open(os.path.join(json_dir, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                all_chunks.extend(data)
    return all_chunks

def build_chroma_db(json_dir, persist_dir="chroma_store"):
    print("初始化嵌入模型...")
    embedder = LocalEmbeddingModel()

    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name="dao_knowledge")

    chunks = load_chunks(json_dir)
    print(f"开始处理 {len(chunks)} 条段落...")
    
    for chunk in tqdm(chunks):
        text = chunk["content"].strip()
        if not text:
            continue
        vector = embedder.embed_text(text)
        collection.add(
            documents=[text],
            embeddings=[vector],
            metadatas=[{
                "id": str(chunk.get("id", "")),
                "title": str(chunk.get("title", "")),
                "chapter_title": str(chunk.get("chapter_title", ""))
            }],
            #ids=[chunk["id"]]
            ids=[str(uuid.uuid4())]
        )

    print(f"✅ 构建完成！数据保存在：{persist_dir}/")

if __name__ == "__main__":
    build_chroma_db("book_split")
