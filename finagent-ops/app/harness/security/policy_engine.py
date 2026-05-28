from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class PolicyContext:
    user_id: str
    business_line: str
    tool_name: str
    attributes: Optional[Dict[str, Any]] = None

@dataclass
class PolicyResult:
    allowed: bool
    reason: str
    matched_policy: Optional[str] = None

class PolicyEngine:
    def __init__(self):
        self._policies = []

    def add_policy(self, name: str, rule: Dict[str, Any]):
        self._policies.append({"name": name, "rule": rule})

    def evaluate(self, context: PolicyContext) -> PolicyResult:
        if not self._policies:
            return PolicyResult(allowed=True, reason="No policies configured")

        for policy in self._policies:
            rule = policy["rule"]
            if self._matches_context(rule, context):
                effect = rule.get("effect", "allow")
                if effect == "deny":
                    return PolicyResult(
                        allowed=False,
                        reason=f"Denied by policy: {policy['name']}",
                        matched_policy=policy["name"],
                    )

        return PolicyResult(allowed=True, reason="Allowed by default")

    def _matches_context(self, rule: Dict, context: PolicyContext) -> bool:
        condition = rule.get("condition", {})
        if "business_line" in condition:
            if context.business_line != condition["business_line"]:
                return False
        if "tool_name" in condition:
            if context.tool_name not in condition["tool_name"]:
                return False
        return True