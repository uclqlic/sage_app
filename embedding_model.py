# embedding_model.py
from transformers import AutoTokenizer, AutoModel
import torch

class LocalEmbeddingModel:
    def __init__(self, model_name="BAAI/bge-small-zh"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

    def embed_text(self, text: str) -> list:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings[0].numpy().tolist()
