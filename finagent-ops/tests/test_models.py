import pytest
from app.models import ModelConfig, Policy, Tool

def test_model_config_can_be_created():
    model = ModelConfig(
        name="Qwen-7B",
        provider="dashscope",
        model_id="qwen-7b",
        endpoint="https://api.dashscope.cn",
        is_active=True,
    )
    assert model.name == "Qwen-7B"
    assert model.is_active is True

def test_policy_has_rule_field():
    policy = Policy(
        name="block-pii",
        rule={"effect": "deny", "condition": {"contains_pii": True}},
    )
    assert policy.rule["effect"] == "deny"