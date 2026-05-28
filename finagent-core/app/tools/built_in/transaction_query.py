from app.tools.registry import global_registry


@global_registry.register(
    name="query_transaction_status",
    description="查询指定交易的状态",
    parameters={
        "type": "object",
        "properties": {
            "transaction_id": {"type": "string", "description": "交易ID"},
        },
        "required": ["transaction_id"],
    },
)
async def query_transaction_status(transaction_id: str, context: dict = None) -> dict:
    """Mock实现：返回交易状态"""
    return {
        "transaction_id": transaction_id,
        "status": "success",
        "amount": "100.00",
        "time": "2024-05-28 10:00:00",
    }