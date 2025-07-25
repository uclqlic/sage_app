import os
import json
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from embedding_model import LocalEmbeddingModel

# 加载角色 persona JSON 文件
def load_personas():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    persona_path = os.path.join(current_dir, "personas.json")
    if not os.path.exists(persona_path):
        raise FileNotFoundError(f"无法找到 personas.json 文件：{persona_path}")
    with open(persona_path, "r", encoding="utf-8") as f:
        return json.load(f)

personas = load_personas()

# 加载 .env 文件中的 OPENAI_API_KEY
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class RAGAgent:
    def __init__(self, persona="孔子"):
        self.embedder = LocalEmbeddingModel()
        self.index = faiss.IndexFlatL2(self.embedder.dim)
        self.documents = []  # list of (text, metadata)
        self.persona = persona
        self.history = []

    def add_documents(self, docs):
        # docs: list of (text, metadata)
        embeddings = [self.embedder.embed_text(text) for text, _ in docs]
        self.index.add(np.array(embeddings, dtype="float32"))
        self.documents.extend(docs)

    def retrieve(self, query, top_k=5):
        embedding = self.embedder.embed_text(query).astype("float32").reshape(1, -1)
        _, indices = self.index.search(embedding, top_k)
        return [self.documents[i] for i in indices[0] if i < len(self.documents)]

    def ask(self, question):
        context_pairs = self.retrieve(question)

        # 获取角色人格
        persona_data = personas.get(self.persona)
        if not persona_data:
            raise ValueError(f"角色 {self.persona} 不存在")

        system_prompt = persona_data["system_prompt"]

        # 构造引用段落
        quote_blocks = ""
        for text, meta in context_pairs:
            book = meta.get("title", "未知书籍").replace(".md", "").replace(".pdf", "")
            chapter = meta.get("chapter_title", "未知章节")
            quote_blocks += f"> {text.strip()}\n> ——《{book}》·{chapter}\n\n"

        user_prompt = f"""
【引用资料】：
{quote_blocks}

【用户问题】：{question}
请以你的风格回答，引用资料内容，不得编造。
"""

        messages = [{"role": "system", "content": system_prompt}]
        for q, a in self.history[-5:]:
            messages.append({"role": "user", "content": q})
            messages.append({"role": "assistant", "content": a})
        messages.append({"role": "user", "content": user_prompt})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )

        answer = response.choices[0].message.content.strip()
        self.history.append((question, answer))
        return answer

if __name__ == "__main__":
    from rich import print
    import streamlit as st
    print("[bold green]RAGAgent ready for use in app.py[/bold green]")
