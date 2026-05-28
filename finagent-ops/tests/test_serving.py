import pytest
from app.harness.serving.router import Router, ComplexityLevel

def test_router_classifies_simple_query():
    router = Router()
    complexity = router.classify_complexity("What is my account balance?")
    assert complexity in [ComplexityLevel.LOW, ComplexityLevel.MEDIUM]

def test_router_classifies_complex_query():
    router = Router()
    complexity = router.classify_complexity("Analyze the financial impact of interest rate changes on our investment portfolio over the last 5 years")
    assert complexity == ComplexityLevel.HIGH

def test_rate_limiter_allows_request_under_limit():
    from app.harness.serving.rate_limiter import RateLimiter
    limiter = RateLimiter(requests_per_minute=60)
    assert limiter.check_limit("business_line_1") is True