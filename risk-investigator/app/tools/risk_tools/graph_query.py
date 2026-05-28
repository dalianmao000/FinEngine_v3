"""Graph query tools for fund flow and relationship analysis."""

from typing import Dict, Any, List
from app.tools.registry import register_tool


MOCK_FUND_FLOW_PATHS = [
    {
        "path_id": "PATH_001",
        "source_user": "user_123",
        "source_account": "ACC_SOURCE_001",
        "destination_user": "user_456",
        "destination_account": "ACC_DEST_001",
        "amount": 50000.00,
        "currency": "CNY",
        "transaction_ids": ["TXN_001", "TXN_002"],
        "hops": 2,
        "risk_score": 90,
        "risk_indicator": "HIGH",
        "description": "大额转账至可疑账户",
    },
    {
        "path_id": "PATH_002",
        "source_user": "user_123",
        "source_account": "ACC_SOURCE_002",
        "destination_user": "user_789",
        "destination_account": "ACC_DEST_002",
        "amount": 2000.00,
        "currency": "CNY",
        "transaction_ids": ["TXN_003"],
        "hops": 1,
        "risk_score": 30,
        "risk_indicator": "LOW",
        "description": "正常转账",
    },
]

MOCK_RELATIONSHIP_GRAPH = {
    "user_id": "user_123",
    "nodes": [
        {
            "user_id": "user_123",
            "account": "ACC_SOURCE_001",
            "relationship": "self",
            "trust_level": "high",
        },
        {
            "user_id": "user_456",
            "account": "ACC_DEST_001",
            "relationship": "stranger",
            "trust_level": "low",
            "interaction_count": 1,
        },
        {
            "user_id": "user_789",
            "account": "ACC_DEST_002",
            "relationship": "acquaintance",
            "trust_level": "medium",
            "interaction_count": 5,
        },
        {
            "user_id": "user_family",
            "account": "ACC_FAMILY_001",
            "relationship": "family",
            "trust_level": "high",
            "interaction_count": 20,
        },
    ],
    "edges": [
        {"source": "user_123", "target": "user_456", "type": "transaction", "weight": 1},
        {"source": "user_123", "target": "user_789", "type": "transaction", "weight": 5},
        {
            "source": "user_123",
            "target": "user_family",
            "type": "family",
            "weight": 20,
        },
    ],
    "suspicious_clusters": [
        {
            "cluster_id": "CLUSTER_001",
            "members": ["user_123", "user_456"],
            "reason": "高风险交易关系",
            "risk_score": 90,
        }
    ],
}


@register_tool("query_fund_flow")
async def query_fund_flow(user_id: str, depth: int = 2) -> Dict[str, Any]:
    """Query fund flow analysis for a user."""
    return {
        "user_id": user_id,
        "depth": depth,
        "paths": MOCK_FUND_FLOW_PATHS,
        "total_paths": len(MOCK_FUND_FLOW_PATHS),
        "high_risk_paths": sum(
            1 for p in MOCK_FUND_FLOW_PATHS if p["risk_indicator"] == "HIGH"
        ),
    }


@register_tool("query_relationship_graph")
async def query_relationship_graph(user_id: str) -> Dict[str, Any]:
    """Query relationship graph for a user."""
    return {
        "user_id": user_id,
        "nodes": MOCK_RELATIONSHIP_GRAPH["nodes"],
        "edges": MOCK_RELATIONSHIP_GRAPH["edges"],
        "suspicious_clusters": MOCK_RELATIONSHIP_GRAPH["suspicious_clusters"],
        "total_connections": len(MOCK_RELATIONSHIP_GRAPH["nodes"]) - 1,
    }