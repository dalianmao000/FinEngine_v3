"""Graph explorer node for querying fund flows and relationship graphs."""

from typing import Dict, Any

from app.graph_rag.cypher_generator import generate_cypher_query
from app.tools.registry import tool_registry


async def graph_explorer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Explore graph relationships and fund flows.

    Args:
        state: The current risk investigation state with collected_evidence

    Returns:
        Updated state dict with graph_query_result and status
    """
    collected_evidence = state.get("collected_evidence", {})
    target_user_id = state.get("target_user_id", "")

    transactions = collected_evidence.get("transaction_history", {}).get(
        "transactions", []
    )

    cypher_query = generate_cypher_query(target_user_id, transactions)

    fund_flow_result = await tool_registry.execute("query_fund_flow", user_id=target_user_id)
    relationship_result = await tool_registry.execute(
        "query_relationship_graph", user_id=target_user_id
    )

    graph_query_result = f"""
=== Fund Flow Analysis ===
Cypher Query Used:
{cypher_query}

=== Fund Flow Paths ===
{fund_flow_result}

=== Relationship Graph ===
{relationship_result}
""".strip()

    return {
        "graph_query_result": graph_query_result,
        "status": "GRAPHING",
    }