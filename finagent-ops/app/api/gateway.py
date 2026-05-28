from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.harness.serving import Router, ComplexityLevel
from app.harness.serving.cache import SemanticCache
from app.harness.serving.rate_limiter import RateLimiter
from app.harness.security.guardrail import Guardrail

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str
    business_line: str = "default"
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    model: str
    cached: bool = False
    tokens_used: int = 0

@router.post("/chat")
async def chat(request: ChatRequest):
    guardrail = Guardrail()
    guard_result = guardrail.check_content(request.prompt)

    if guard_result.is_blocked:
        raise HTTPException(status_code=400, detail=f"Content blocked: {guard_result.detected_types}")

    routing = Router()
    complexity = routing.classify_complexity(request.prompt)
    model = routing.route_model(complexity)

    return ChatResponse(
        response=f"[Mock response from {model}] {request.prompt[:50]}...",
        model=model,
        cached=False,
        tokens_used=len(request.prompt.split()) * 2,
    )

@router.get("/cache/stats")
async def cache_stats():
    return {"hits": 100, "misses": 200, "hit_rate": 0.33}

@router.delete("/cache")
async def clear_cache():
    return {"status": "cleared"}