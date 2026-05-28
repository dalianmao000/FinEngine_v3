from app.rag.embedding import EmbeddingClient
from app.rag.knowledge_base import KnowledgeBase


class SimpleRetriever:
    """简单检索器（纯向量检索）"""

    def __init__(self, knowledge_base: KnowledgeBase, embedding_client: EmbeddingClient):
        self.kb = knowledge_base
        self.embedding = embedding_client

    async def retrieve(
        self, query: str, top_k: int = 5, filter: dict = None
    ) -> list[dict]:
        query_embedding = await self.embedding.encode(query)
        results = self.kb.search(query_embedding, top_k=top_k, filter=filter)
        return results
