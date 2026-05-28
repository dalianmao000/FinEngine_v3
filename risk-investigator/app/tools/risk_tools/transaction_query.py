"""Transaction query tools for risk investigation."""

from typing import Dict, List, Any
from app.tools.registry import register_tool


MOCK_TRANSACTIONS = [
    {
        "transaction_id": "TXN_001",
        "user_id": "user_123",
        "amount": 50000.00,
        "currency": "CNY",
        "recipient": "陌生账户",
        "recipient_account": "ACC_SUSPICIOUS_001",
        "timestamp": "2026-05-27T14:30:00Z",
        "type": "TRANSFER",
        "status": "COMPLETED",
        "risk_indicator": "HIGH",
        "description": "大额转账至陌生账户",
    },
    {
        "transaction_id": "TXN_002",
        "user_id": "user_123",
        "amount": 150.00,
        "currency": "CNY",
        "recipient": "在线商户",
        "recipient_account": "ACC_MERCHANT_001",
        "timestamp": "2026-05-26T10:15:00Z",
        "type": "PAYMENT",
        "status": "COMPLETED",
        "risk_indicator": "LOW",
        "description": "正常消费",
    },
    {
        "transaction_id": "TXN_003",
        "user_id": "user_123",
        "amount": 80.00,
        "currency": "CNY",
        "recipient": "在线商户",
        "recipient_account": "ACC_MERCHANT_002",
        "timestamp": "2026-05-25T16:45:00Z",
        "type": "PAYMENT",
        "status": "COMPLETED",
        "risk_indicator": "LOW",
        "description": "正常消费",
    },
    {
        "transaction_id": "TXN_004",
        "user_id": "user_123",
        "amount": 2000.00,
        "currency": "CNY",
        "recipient": "家人账户",
        "recipient_account": "ACC_FAMILY_001",
        "timestamp": "2026-05-24T09:00:00Z",
        "type": "TRANSFER",
        "status": "COMPLETED",
        "risk_indicator": "LOW",
        "description": "正常转账",
    },
    {
        "transaction_id": "TXN_005",
        "user_id": "user_123",
        "amount": 500.00,
        "currency": "CNY",
        "recipient": "朋友账户",
        "recipient_account": "ACC_FRIEND_001",
        "timestamp": "2026-05-23T20:30:00Z",
        "type": "TRANSFER",
        "status": "COMPLETED",
        "risk_indicator": "LOW",
        "description": "正常转账",
    },
]


@register_tool("get_transaction_history")
async def get_transaction_history(user_id: str, limit: int = 10) -> Dict[str, Any]:
    """Get transaction history for a user."""
    user_transactions = [
        tx for tx in MOCK_TRANSACTIONS if tx["user_id"] == user_id
    ][:limit]
    return {
        "user_id": user_id,
        "transactions": user_transactions,
        "total_count": len(user_transactions),
        "risk_summary": {
            "high_risk_count": sum(
                1 for tx in user_transactions if tx["risk_indicator"] == "HIGH"
            ),
            "total_amount": sum(tx["amount"] for tx in user_transactions),
        },
    }


@register_tool("get_transaction_detail")
async def get_transaction_detail(transaction_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific transaction."""
    for tx in MOCK_TRANSACTIONS:
        if tx["transaction_id"] == transaction_id:
            return tx
    return {
        "error": "Transaction not found",
        "transaction_id": transaction_id,
    }