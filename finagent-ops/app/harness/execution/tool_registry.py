import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Tool:
    id: str = None
    name: str = ""
    description: str = ""
    endpoint: str = ""
    rbac_roles: List[str] = None
    timeout_seconds: int = 30
    is_active: bool = True

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.rbac_roles is None:
            self.rbac_roles = []

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())

    def check_access(self, tool_name: str, user_role: str) -> bool:
        tool = self._tools.get(tool_name)
        if not tool:
            return False
        if not tool.rbac_roles:
            return True
        return user_role in tool.rbac_roles