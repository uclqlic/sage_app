import os
import openai
from dotenv import load_dotenv
import numpy as np

load_dotenv()

class LocalEmbeddingModel:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def embed(self, text):
        response = openai.embeddings.create(
            input=text,
            model="text-embedding-3-small"  # 更轻量的新模型
        )
        return np.array(response.data[0].embedding)
