import json
import faiss
import numpy as np
import streamlit as st
from openai import OpenAI
from sentence_transformers import SentenceTransformer

# 加载人物 personas.json 文件
def load_personas():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    persona_path = os.path.join(current_dir, "personas.json")
    if not os.path.exists(persona_path):
        raise FileNotFoundError(f"无法找到 personas.json 文件：{persona_path}")
    with open(persona_path, "r", encoding="utf-8") as f:
        return json.load(f)

class RAGAgent:
    def __init__(self, persona=None):
        # 初始化 Sentence Transformer 模型（可以选择其他模型）
        self.embedder = SentenceTransformer('paraphrase-MiniLM-L6-v2')

        # 初始化 FAISS 向量检索
        self.index = faiss.IndexFlatL2(384)  # 假设嵌入维度为 384
        self.documents = []
        self.history = []

        # 使用 Streamlit Secrets 获取 OpenAI API 密钥
        self.openai_client = OpenAI(api_key=st.secrets["openai"]["api_key"])

        # 加载 persona
        self.personas = load_personas()
        if persona is None:
            self.persona = self.personas.get("孔子")
        else:
            self.persona = self.personas.get(persona)

    def add_documents(self, docs):
        embeddings = [self.embedder.encode(text) for text, _ in docs]
        embeddings = np.array(embeddings, dtype=np.float32)
        self.index.add(embeddings)
        self.documents.extend(docs)

    def retrieve(self, query, top_k=5):
        query_embedding = self.embedder.encode(query).reshape(1, -1)
        _, indices = self.index.search(query_embedding, top_k)
        return [self.documents[i] for i in indices[0]]

    def ask(self, question):
        context_pairs = self.retrieve(question)
        system_prompt = self.persona["system_prompt"]

        # 构造引用段落
        quote_blocks = ""
        for text, meta in context_pairs:
            book = meta.get("title", "未知书籍").replace(".md", "").replace(".pdf", "")
            chapter = meta.get("chapter_title", "未知章节")
            quote_blocks += f"> {text.strip()}\n> ——《{book}》·{chapter}\n\n"

        # 构造用户 prompt
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

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )

        answer = response.choices[0].message.content.strip()
        self.history.append((question, answer))
        return answer

# 命令行测试入口
if __name__ == "__main__":
    personas = load_personas()
    persona_id = "孔子"
    agent = RAGAgent(persona=persona_id)
    while True:
        question = input("\n🤖 请输入你的问题（输入 q 退出）：\n> ")
        if question.lower() in ['q', 'quit', 'exit']:
            break
        answer = agent.ask(question)
        print(f"\n💡 回答（{persona_id}）：\n{answer}")
