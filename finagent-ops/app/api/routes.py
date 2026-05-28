from fastapi import APIRouter

from app.api import gateway, eval, admin

api_router = APIRouter()

api_router.include_router(gateway.router, tags=["gateway"])
api_router.include_router(eval.router, tags=["eval"])
api_router.include_router(admin.router, tags=["admin"])

@api_router.get("/health")
async def health():
    return {"status": "healthy", "service": "finagent-ops"}