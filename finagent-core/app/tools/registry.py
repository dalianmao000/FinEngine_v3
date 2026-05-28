from typing import Callable, Any, Optional
from dataclasses import dataclass
import inspect


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict
    handler: Callable
    required_roles: list[str] = None
    timeout_ms: int = 5000


class ToolRegistry:
    """工具注册中心"""

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict,
        required_roles: list[str] = None,
        timeout_ms: int = 5000,
    ):
        def decorator(func: Callable):
            tool_def = ToolDefinition(
                name=name,
                description=description,
                parameters=parameters,
                handler=func,
                required_roles=required_roles or [],
                timeout_ms=timeout_ms,
            )
            self._tools[name] = tool_def
            return func
        return decorator

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    async def execute(self, name: str, parameters: dict, context: dict) -> Any:
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")

        if tool.required_roles:
            user_role = context.get("user_role", "guest")
            if user_role not in tool.required_roles:
                raise PermissionError(f"User role '{user_role}' not authorized for tool '{name}'")

        sig = inspect.signature(tool.handler)
        if "context" in sig.parameters:
            result = await tool.handler(**parameters, context=context)
        else:
            result = await tool.handler(**parameters)

        return result


global_registry = ToolRegistry()