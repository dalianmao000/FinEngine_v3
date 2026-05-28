from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.harness.security.policy_engine import PolicyEngine, PolicyContext

router = APIRouter()
policy_engine = PolicyEngine()

class PolicyRequest(BaseModel):
    name: str
    description: str = ""
    rule: dict

class PolicyResponse(BaseModel):
    id: str
    name: str
    allowed: bool
    reason: str

@router.post("/policies")
async def create_policy(request: PolicyRequest):
    policy_engine.add_policy(request.name, request.rule)
    return {"status": "created", "name": request.name}

@router.get("/policies")
async def list_policies():
    return {"policies": []}

@router.post("/guardrail/check")
async def check_guardrail(content: dict):
    from app.harness.security.guardrail import Guardrail
    guardrail = Guardrail()
    result = guardrail.check_content(content.get("text", ""))

    return {
        "is_blocked": result.is_blocked,
        "detected_types": result.detected_types,
        "sanitized_content": result.sanitized_content,
    }