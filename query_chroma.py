# query_chroma.py
import chromadb
from embedding_model import LocalEmbeddingModel

class ChromaSearcher:
    def __init__(self, persist_dir="chroma_store"):
        self.embedder = LocalEmbeddingModel()
        self.client = chromadb.PersistentClient(path=persist_dir)  # ✅ 新写法
        self.collection = self.client.get_or_create_collection(name="dao_knowledge")

    def search(self, query, top_k=3):
        embedding = self.embedder.embed_text(query)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        return results

if __name__ == "__main__":
    searcher = ChromaSearcher()

    while True:
        query = input("\n请输入你的问题（输入 q 退出）：\n> ")
        if query.strip().lower() in ["q", "quit", "exit"]:
            break
        results = searcher.search(query)

        print("\n🔎 最相关段落：")
        for i in range(len(results['documents'][0])):
            print(f"\n--- 结果 {i+1} ---")
            print(f"标题：{results['metadatas'][0][i].get('title')}")
            print(f"章节：{results['metadatas'][0][i].get('chapter_title')}")
            print(f"段落：{results['documents'][0][i]}")
