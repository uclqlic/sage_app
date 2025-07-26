import os
import json
import faiss
import numpy as np
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
    def __init__(self, persona=None, persist_dir="faiss_index"):
        # 初始化本地向量检索
        self.embedder = LocalEmbeddingModel()
        self.index = faiss.IndexFlatL2(self.embedder.dim)
        self.documents = []  # [(text, metadata)] 用于存储文档
        self.persona = persona
        self.history = []

        # 初始化 OpenAI 客户端
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        添加文档到 FAISS 索引。
        docs: [(text, metadata)]
        """
        embeddings = [self.embedder.embed_text(text) for text, _ in docs]
        self.index.add(np.array(embeddings, dtype="float32"))
        self.documents.extend(docs)

    def retrieve(self, query, top_k=5):
        """
        根据查询文本从 FAISS 索引中检索相关文档。
        """
        # 将查询文本转换为嵌入
        embedding = self.embedder.embed_text(query).astype("float32").reshape(1, -1)

        # 执行 FAISS 查询，获取最近的 top_k 个索引
        _, indices = self.index.search(embedding, top_k)

        # 返回根据查询索引获取到的文档，处理索引越界的情况
        result_documents = []
        for i in indices[0]:
            if i < len(self.documents):  # 确保索引不超出文档范围
                result_documents.append(self.documents[i])
        
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
