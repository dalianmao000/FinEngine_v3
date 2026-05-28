class FinAgentOpsError(Exception):
    """Base exception for FinAgent-Ops"""
    pass

class CacheError(FinAgentOpsError):
    """Cache-related errors"""
    pass

class PolicyViolationError(FinAgentOpsError):
    """Policy violation detected"""
    pass

class ToolExecutionError(FinAgentOpsError):
    """Tool execution failed"""
    pass

class RateLimitExceededError(FinAgentOpsError):
    """Rate limit exceeded"""
    pass