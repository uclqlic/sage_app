import os
import json
import streamlit as st
from openai import OpenAI
from embedding_model import LocalEmbeddingModel
import chromadb

# 加载人物 personas.json 文件
def load_personas():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    persona_path = os.path.join(current_dir, "personas.json")
    if not os.path.exists(persona_path):
        raise FileNotFoundError(f"无法找到 personas.json 文件：{persona_path}")
    with open(persona_path, "r", encoding="utf-8") as f:
        return json.load(f)

class RAGAgent:
    def __init__(self, persona=None, persist_dir="chromadb_index"):
        # 初始化 LocalEmbeddingModel 用于文本嵌入
        self.embedder = LocalEmbeddingModel()

        # 使用 chromadb 初始化向量数据库
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(name="dao_knowledge")  # 创建或获取数据库集合
        self.documents = []  # [(text, metadata)] 用于存储文档
        self.persona = persona
        self.history = []

        # 使用 Streamlit Secrets 获取 OpenAI API 密钥
        self.openai_client = OpenAI(api_key=st.secrets["openai"]["api_key"])

        # 加载 persona
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

    def add_documents(self, docs):
        """
        添加文档到 chromadb 数据库。
        docs: [(text, metadata)]
        """
        # 获取文档的嵌入表示
        embeddings = [self.embedder.embed_text(text) for text, _ in docs]
        
        # 使用 chromadb 存储嵌入和文档
        for doc, embedding in zip(docs, embeddings):
            self.collection.add(
                documents=[doc[0]],  # 文本
                metadatas=[doc[1]],   # 元数据
                embeddings=[embedding]  # 嵌入
            )
        self.documents.extend(docs)

    def retrieve(self, query, top_k=5):
        """
        根据查询文本从 chromadb 中检索相关文档。
        """
        # 将查询文本转换为嵌入
        embedding = self.embedder.embed_text(query)
        
        # 使用 chromadb 查询相关的 top_k 个文档
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        
        # 检查结果并返回有效文档
        result_documents = []
        for text, meta in zip(results["documents"][0], results["metadatas"][0]):
            result_documents.append((text, meta))
        
        if len(result_documents) == 0:
            st.warning("没有找到相关文档")
            return []

        return result_documents

    def ask(self, question):
        """
        向 OpenAI 请求生成回答，并基于已有的文档返回引用内容。
        """
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

        # 消息列表，包含系统提示和对话历史
        messages = [{"role": "system", "content": system_prompt}]
        for q, a in self.history[-5:]:
            messages.append({"role": "user", "content": q})
            messages.append({"role": "assistant", "content": a})
        messages.append({"role": "user", "content": user_prompt})

        # 使用 OpenAI API 获取回答
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )

        answer = response.choices[0].message.content.strip()
        self.history.append((question, answer))
        return answer

# ===== 命令行测试入口（非 streamlit 时使用） =====
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

print("🔍 当前 OpenAI Key 来自 secrets：", st.secrets["openai"]["api_key"])
