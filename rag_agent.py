import os
import json
import faiss
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

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

        # 加载 OpenAI API 密钥
        load_dotenv()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

        # 构
