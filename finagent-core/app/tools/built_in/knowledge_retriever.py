from app.tools.registry import global_registry


@global_registry.register(
    name="knowledge_retriever",
    description="检索知识库中的相关内容",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "查询内容"},
        },
        "required": ["query"],
    },
)
async def knowledge_retriever(query: str, context: dict = None) -> dict:
    """Mock实现：返回知识检索结果"""
    return {
        "query": query,
        "results": [
            {"content": "相关知识条目1", "source": "知识库"},
            {"content": "相关知识条目2", "source": "知识库"},
        ]
    }