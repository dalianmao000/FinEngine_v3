import os
import glob
import yaml
from pathlib import Path
from typing import Optional


class SafetyPolicyManager:
    """支持运行时动态更新安全策略"""

    def __init__(self, policy_path: str = "app/scenarios/*/safety.yaml"):
        self.policy_path = policy_path
        self._cache: dict[str, dict] = {}
        self._last_modified: dict[str, float] = {}

    def get_policy(self, scenario: str) -> dict:
        patterns = glob.glob(self.policy_path.replace("*", scenario))
        if not patterns:
            return self._get_default_policy()

        policy_file = patterns[0]
        mtime = os.path.getmtime(policy_file)

        if self._last_modified.get(policy_file, 0) < mtime:
            with open(policy_file, "r", encoding="utf-8") as f:
                policy = yaml.safe_load(f) or {}
            self._cache[scenario] = policy
            self._last_modified[policy_file] = mtime

        return self._cache.get(scenario, self._get_default_policy())

    def _get_default_policy(self) -> dict:
        return {
            "level": "medium",
            "block_words": [],
            "require_human_confirm": [],
        }