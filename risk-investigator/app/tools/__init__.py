"""Tools module for Risk Investigator."""

# Import all tools to register them
from app.tools.risk_tools import transaction_query
from app.tools.risk_tools import device_fingerprint
from app.tools.risk_tools import ip_profiler
from app.tools.risk_tools import blacklist_check
from app.tools.risk_tools import graph_query

# Import registry after tools are loaded to avoid circular imports
from app.tools.registry import tool_registry, register_tool

__all__ = ["tool_registry", "register_tool"]