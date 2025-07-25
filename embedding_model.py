from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

class LocalEmbeddingModel:
    def __init__(self, model_name="BAAI/bge-small-zh"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.dim = self.model.config.hidden_size  # e.g., 384 for bge-small-zh

    def embed_text(self, text: str) -> np.ndarray:
        # 使用模型生成 embedding（池化 + normalize）
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            last_hidden_state = outputs.last_hidden_state  # (1, seq_len, hidden)
            attention_mask = inputs["attention_mask"].unsqueeze(-1)  # (1, seq_len, 1)
            masked_embeddings = last_hidden_state * attention_mask
            sum_embeddings = masked_embeddings.sum(dim=1)
            sum_mask = attention_mask.sum(dim=1)
            embedding = sum_embeddings / sum_mask  # mean pooling

        embedding = embedding[0].cpu().numpy()
        embedding = embedding / np.linalg.norm(embedding)  # normalize
        return embedding.astype("float32")  # ✅ 必须是 float32
