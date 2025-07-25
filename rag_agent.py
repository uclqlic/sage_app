import os
import json
import chromadb
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from embedding_model import LocalEmbeddingModel

st.set_page_config(
    page_title="Dao AI - Answer your question in Chinese Wisdom",
    page_icon="🏮",
    layout="centered",
    initial_sidebar_state="expanded"   # ✅ 改成 expanded
)

# 加载 .env 文件中的 OPENAI_API_KEY
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 加载角色 persona JSON 文件（动态路径）
def load_personas():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    persona_path = os.path.join(current_dir, "personas.json")
    if not os.path.exists(persona_path):
        raise FileNotFoundError(f"无法找到 personas.json 文件：{persona_path}")
    with open(persona_path, "r", encoding="utf-8") as f:
        return json.load(f)

class RAGAgent:
    def __init__(self, persona=None, persist_dir="chroma_store"):
        self.embedder = LocalEmbeddingModel()
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name="dao_knowledge")
        self.history = []

        # 加载或指定人物 persona
        self.personas = load_personas()
        if persona is None:
            self.persona = self.personas.get("孔子")
        elif isinstance(persona, dict):
            self.persona = persona
        elif isinstance(persona, str):
            self.persona = self.personas.get(persona)
        else:
            raise ValueError("Invalid persona input")

        if not self.persona:
            raise ValueError("角色 persona 加载失败")

    def retrieve(self, query, top_k=5):
        embedding = self.embedder.embed_text(query)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        return list(zip(results["documents"][0], results["metadatas"][0]))

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

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )

        answer = response.choices[0].message.content.strip()
        self.history.append((question, answer))
        return answer

if __name__ == "__main__":
    personas = load_personas()
    persona_id = st.selectbox("请选择导师：", list(personas.keys()), index=0)
    agent = RAGAgent(persona=persona_id)
    while True:
        question = input("\n🤖 请输入你的问题（输入 q 退出）：\n> ")
        if question.lower() in ['q', 'quit', 'exit']:
            break
        answer = agent.ask(question)
        print(f"\n💡 回答（{persona_id}）：\n{answer}")
