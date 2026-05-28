from app.tools.registry import global_registry


@global_registry.register(
    name="freeze_card",
    description="冻结指定银行卡（高风险操作，需人工确认）",
    parameters={
        "type": "object",
        "properties": {
            "card_id": {"type": "string", "description": "卡号"},
            "reason": {"type": "string", "description": "冻结原因"},
        },
        "required": ["card_id"],
    },
    required_roles=["admin"],
)
async def freeze_card(card_id: str, reason: str = "", context: dict = None) -> dict:
    """Mock实现：返回卡片冻结结果"""
    return {
        "card_id": card_id,
        "status": "frozen",
        "reason": reason,
        "require_human_confirm": True,
    }