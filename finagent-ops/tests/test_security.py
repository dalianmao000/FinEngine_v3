from app.harness.security.guardrail import Guardrail
from app.harness.security.policy_engine import PolicyEngine, PolicyContext

def test_guardrail_blocks_pii():
    guardrail = Guardrail()
    result = guardrail.check_content("My credit card is 1234-5678-9012-3456")
    assert result.is_blocked is True
    assert "card_number" in result.detected_types

def test_policy_engine_allows_valid_request():
    engine = PolicyEngine()
    context = PolicyContext(
        user_id="user123",
        business_line="customer_service",
        tool_name="query_account",
    )
    result = engine.evaluate(context)
    assert result.allowed is True