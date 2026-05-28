from sentence_transformers import SentenceTransformer


class EmbeddingClient:
    """向量化客户端（使用本地模型）"""

    def __init__(self, model_name: str = "shibing624/text2vec-base-chinese"):
        self.model = SentenceTransformer(model_name)

    async def encode(self, text: str) -> list[float]:
        embedding = self.model.encode(text)
        return embedding.tolist()

    async def encode_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
