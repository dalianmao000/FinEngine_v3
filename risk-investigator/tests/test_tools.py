"""Tests for risk investigation tools."""

import pytest
from app.tools.registry import tool_registry, register_tool


@pytest.mark.asyncio
async def test_tool_registry_register():
    """Test that tools can be registered in the registry."""
    test_tools_count = len(tool_registry.list_tools())

    @register_tool("test_tool")
    async def test_func():
        return {"result": "ok"}

    assert "test_tool" in tool_registry.list_tools()
    assert len(tool_registry.list_tools()) == test_tools_count + 1


@pytest.mark.asyncio
async def test_tool_registry_execute_async():
    """Test executing an async tool."""
    result = await tool_registry.execute("get_transaction_history", user_id="user_123")
    assert "user_id" in result
    assert "transactions" in result
    assert result["user_id"] == "user_123"


@pytest.mark.asyncio
async def test_tool_registry_list_tools():
    """Test listing all registered tools."""
    tools = tool_registry.list_tools()
    expected_tools = [
        "get_transaction_history",
        "get_transaction_detail",
        "get_device_fingerprint",
        "get_ip_profile",
        "check_blacklist",
        "query_fund_flow",
        "query_relationship_graph",
    ]
    for tool_name in expected_tools:
        assert tool_name in tools


@pytest.mark.asyncio
async def test_tool_registry_execute_not_found():
    """Test executing a non-existent tool raises error."""
    with pytest.raises(ValueError, match="Tool .* not found"):
        await tool_registry.execute("nonexistent_tool", arg="value")


@pytest.mark.asyncio
async def test_get_transaction_history():
    """Test get_transaction_history returns expected structure."""
    result = await tool_registry.execute("get_transaction_history", user_id="user_123")
    assert result["user_id"] == "user_123"
    assert "transactions" in result
    assert "total_count" in result
    assert "risk_summary" in result


@pytest.mark.asyncio
async def test_get_transaction_detail():
    """Test get_transaction_detail returns expected structure."""
    result = await tool_registry.execute(
        "get_transaction_detail", transaction_id="TXN_001"
    )
    assert result["transaction_id"] == "TXN_001"
    assert result["amount"] == 50000.00
    assert result["recipient"] == "陌生账户"
    assert result["risk_indicator"] == "HIGH"


@pytest.mark.asyncio
async def test_get_transaction_detail_not_found():
    """Test get_transaction_detail for non-existent transaction."""
    result = await tool_registry.execute(
        "get_transaction_detail", transaction_id="TXN_INVALID"
    )
    assert "error" in result


@pytest.mark.asyncio
async def test_get_device_fingerprint():
    """Test get_device_fingerprint returns expected structure."""
    result = await tool_registry.execute(
        "get_device_fingerprint", user_id="user_123"
    )
    assert result["user_id"] == "user_123"
    assert "device_id" in result
    assert "risk_level" in result
    assert result["risk_level"] == "HIGH"


@pytest.mark.asyncio
async def test_get_ip_profile():
    """Test get_ip_profile returns expected structure."""
    result = await tool_registry.execute("get_ip_profile", user_id="user_123")
    assert result["user_id"] == "user_123"
    assert "ip_address" in result
    assert "is_proxy" in result
    assert "is_datacenter" in result
    assert result["is_proxy"] is True
    assert result["is_datacenter"] is True


@pytest.mark.asyncio
async def test_check_blacklist_user_not_blacklisted():
    """Test check_blacklist for non-blacklisted user."""
    result = await tool_registry.execute("check_blacklist", user_id="user_123")
    assert result["is_blacklisted"] is False
    assert result["blacklist_type"] is None


@pytest.mark.asyncio
async def test_check_blacklist_user_blacklisted():
    """Test check_blacklist for blacklisted user."""
    result = await tool_registry.execute("check_blacklist", user_id="user_999")
    assert result["is_blacklisted"] is True
    assert result["blacklist_type"] == "user"
    assert result["details"]["reason"] == "涉嫌欺诈"


@pytest.mark.asyncio
async def test_check_blacklist_ip_blacklisted():
    """Test check_blacklist for blacklisted IP."""
    result = await tool_registry.execute(
        "check_blacklist", ip_address="203.0.113.1"
    )
    assert result["is_blacklisted"] is True
    assert result["blacklist_type"] == "ip"


@pytest.mark.asyncio
async def test_query_fund_flow():
    """Test query_fund_flow returns expected structure."""
    result = await tool_registry.execute("query_fund_flow", user_id="user_123")
    assert result["user_id"] == "user_123"
    assert "paths" in result
    assert "total_paths" in result
    assert len(result["paths"]) == 2
    assert result["high_risk_paths"] == 1


@pytest.mark.asyncio
async def test_query_relationship_graph():
    """Test query_relationship_graph returns expected structure."""
    result = await tool_registry.execute(
        "query_relationship_graph", user_id="user_123"
    )
    assert result["user_id"] == "user_123"
    assert "nodes" in result
    assert "edges" in result
    assert "suspicious_clusters" in result
    assert len(result["nodes"]) == 4
    assert len(result["suspicious_clusters"]) == 1