from sentence_transformers import SentenceTransformer

class LocalEmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

    @property
    def dim(self):
        return self.model.get_sentence_embedding_dimension()

    def embed_text(self, text):
        return self.model.encode(text, normalize_embeddings=True)
