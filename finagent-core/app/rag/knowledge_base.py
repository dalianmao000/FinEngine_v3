import chromadb
from chromadb.config import Settings
import os


class KnowledgeBase:
    """ChromaDB知识库管理"""

    def __init__(self, persist_directory: str = "./data/chroma"):
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name="knowledge",
            metadata={"description": "金融知识库"},
        )

    def add_documents(self, documents: list[dict]):
        """添加文档

        documents: [{"id": "doc1", "content": "...", "metadata": {...}}]
        """
        ids = [doc["id"] for doc in documents]
        contents = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        self.collection.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas,
        )

    def search(
        self, query_embedding: list[float], top_k: int = 5, filter: dict = None
    ) -> list[dict]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter,
        )

        return [
            {
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            }
            for i in range(len(results["ids"][0]))
        ]

    def count(self) -> int:
        return self.collection.count()
