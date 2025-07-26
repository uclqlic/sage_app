import os
import json
import faiss
import numpy as np
from openai import OpenAI
from embedding_model import LocalEmbeddingModel

# 加载人物设定
def load_personas():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    persona_path = os.path.join(current_dir, "personas.json")
    if not os.path.exists(persona_path):
        raise FileNotFoundError(f"无法找到 personas.json 文件：{persona_path}")
    with open(persona_path, "r", encoding="utf-8") as f:
        return json.load(f)

personas = load_personas()

# 直接从环境变量中获取 OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("未在环境变量中找到 OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

class RAGAgent:
    def __init__(self, persona="孔子"):
        self.embedder = LocalEmbeddingModel()
        self.index = faiss.IndexFlatL2(self.embedder.dim)
        self.documents = []  # [(text, metadata)]
        self.persona = persona
        self.history = []

        # ✅ 添加默认文档，避免空 index 报错
        self.add_documents([
            ("道可道，非常道；名可名，非常名。", {"title": "道德经", "chapter_title": "第一章"}),
            ("学而时习之，不亦说乎？", {"title": "论语", "chapter_title": "学而篇"})
        ])

    def add_documents(self, docs):
        embeddings = [self.embedder.embed_text(text) for text, _ in docs]
        self.index.add(np.array(embeddings, dtype="float32"))
        self.documents.extend(docs)

    def retrieve(self, query, top_k=5):
        if self.index.ntotal == 0:
            return []
        embedding = self.embedder.embed_text(query).astype("float32").reshape(1, -1)
        _, indices = self.index.search(embedding, top_k)
        return [self.documents[i] for i in indices[0] if i < len(self.documents)]

    def ask(self, question):
        context_pairs = self.retrieve(question)

        persona_data = personas.get(self.persona)
        if not persona_data:
            raise ValueError(f"角色 {self.persona} 不存在")

        system_prompt = persona_data["system_prompt"]

        # 构造引用段
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

# ✅ CLI 测试入口（可选）
if __name__ == "__main__":
    agent = RAGAgent()
    while True:
        question = input("\n🤖 请输入你的问题（输入 q 退出）：\n> ")
        if question.lower() in ['q', 'quit', 'exit']:
            break
        role_id = input("请选择角色（孔子 / 老子 / 南怀瑾）：\n> ") or "孔子"
        agent.persona = role_id
        answer = agent.ask(question)
        print(f"\n💡 回答（{role_id}）：\n{answer}")
