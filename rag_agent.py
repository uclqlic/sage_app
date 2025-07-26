import os
import json
import streamlit as st
from pymilvus import Collection, CollectionSchema, FieldSchema, DataType
from openai import OpenAI
from embedding_model import LocalEmbeddingModel

# 加载人物 personas.json 文件
def load_personas():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    persona_path = os.path.join(current_dir, "personas.json")
    if not os.path.exists(persona_path):
        raise FileNotFoundError(f"无法找到 personas.json 文件：{persona_path}")
    with open(persona_path, "r", encoding="utf-8") as f:
        return json.load(f)

class RAGAgent:
    def __init__(self, persona=None, persist_dir="milvus_index"):
        # 初始化 OpenAI 客户端
        self.embedder = LocalEmbeddingModel()
        self.openai_client = OpenAI(api_key=st.secrets["openai"]["api_key"])

        # 初始化 Milvus 客户端
        self.client = Milvus("tcp://localhost:19530")
        schema = CollectionSchema([
            FieldSchema(name="text", dtype=DataType.STRING),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.embedder.dim)
        ], "text")
        self.collection = self.client.create_collection("documents", schema)
        
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
        
        self.history = []

    def add_documents(self, docs):
        """
        添加文档到 Milvus 索引。
        docs: [(text, metadata)]
        """
        embeddings = [self.embedder.embed_text(text) for text, _ in docs]
        self.collection.insert([docs, embeddings])

    def retrieve(self, query, top_k=5):
        """
        根据查询文本从 Milvus 索引中检索相关文档。
        """
        embedding = self.embedder.embed_text(query).astype("float32").reshape(1, -1)
    
        # 执行 Milvus 查询，获取最近的 top_k 个索引
        search_params = {"nprobe": 10}
        results = self.collection.search([embedding], "vector", search_params, limit=top_k)
    
        # 返回检索到的文档
        result_documents = []
        for result in results[0]:
            result_documents.append(result.id)  # 返回文档 ID 和内容
    
        return result_documents

    def ask(self, question):
        """
        向 OpenAI 请求生成回答，并基于已有的文档返回引用内容。
        """
        context_pairs = self.retrieve(question)
        system_prompt = self.persona["system_prompt"]

        # 构造引用段落
        quote_blocks = ""
        for doc in context_pairs:
            quote_blocks += f"> {doc.strip()}\n"

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
