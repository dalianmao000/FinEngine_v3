"""Tool registry for risk investigation tools."""

from typing import Dict, Callable, Any, List
import asyncio


class ToolRegistry:
    """Registry for managing and executing tools."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable):
        """Register a tool with a given name."""
        self._tools[name] = func

    async def execute(self, name: str, **kwargs) -> Any:
        """Execute a tool by name with given arguments."""
        if name not in self._tools:
            raise ValueError(f"Tool {name} not found")
        func = self._tools[name]
        if asyncio.iscoroutinefunction(func):
            return await func(**kwargs)
        return func(**kwargs)

    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())


# Global registry instance
tool_registry = ToolRegistry()


def register_tool(name: str):
    """Decorator to register a tool function."""

    def decorator(func: Callable):
        tool_registry.register(name, func)
        return func

    return decorator