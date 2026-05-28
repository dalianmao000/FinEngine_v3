import pytest
from app.harness.execution.tool_registry import ToolRegistry, Tool
from app.harness.execution.sandbox import Sandbox, ExecutionResult

def test_tool_registry_registers_tool():
    registry = ToolRegistry()
    tool = Tool(
        name="query_account",
        description="Query account balance",
        endpoint="http://internal/api/account",
        rbac_roles=["customer_service"],
    )
    registry.register(tool)
    assert registry.get_tool("query_account") is not None

def test_tool_registry_enforces_rbac():
    registry = ToolRegistry()
    registry.register(Tool(
        name="admin_tool",
        rbac_roles=["admin"],
    ))
    result = registry.check_access("admin_tool", "user_role")
    assert result is False
    result = registry.check_access("admin_tool", "admin")
    assert result is True

@pytest.mark.asyncio
async def test_sandbox_enforces_timeout():
    sandbox = Sandbox()
    result = await sandbox.execute("import time; time.sleep(10)", timeout_seconds=1)
    assert result.timed_out is True