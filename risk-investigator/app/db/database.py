from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON, func, select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, InvestigationTask, AuditLog


engine = None
async_session_maker = None


def create_engine_async(database_url: str):
    global engine, async_session_maker
    engine = create_async_engine(database_url, echo=False, future=True)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine


async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency for getting async session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def save_investigation_task(task_data: dict) -> InvestigationTask:
    """Save or update an investigation task."""
    async with async_session_maker() as session:
        async with session.begin():
            task = InvestigationTask(
                task_id=task_data["task_id"],
                target_user_id=task_data["target_user_id"],
                trigger_event=task_data["trigger_event"],
                status=task_data.get("status", "pending"),
                risk_level=task_data.get("risk_level"),
                final_report_json=str(task_data.get("final_report_json")) if task_data.get("final_report_json") else None,
                human_approval_needed=task_data.get("human_approval_needed", False),
                approval_result=task_data.get("approval_result"),
                approver_id=task_data.get("approver_id"),
                approval_comment=task_data.get("approval_comment"),
                completed_at=datetime.utcnow() if task_data.get("completed_at") else None,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task


async def get_investigation_task(task_id: str) -> Optional[dict]:
    """Get an investigation task by task_id."""
    async with async_session_maker() as session:
        result = await session.execute(
            select(InvestigationTask).where(InvestigationTask.task_id == task_id)
        )
        task = result.scalar_one_or_none()
        if task:
            return {
                "id": task.id,
                "task_id": task.task_id,
                "target_user_id": task.target_user_id,
                "trigger_event": task.trigger_event,
                "status": task.status,
                "risk_level": task.risk_level,
                "final_report_json": task.final_report_json,
                "human_approval_needed": task.human_approval_needed,
                "approval_result": task.approval_result,
                "approver_id": task.approver_id,
                "approval_comment": task.approval_comment,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            }
        return None


async def update_investigation_task(task_id: str, update_data: dict) -> Optional[dict]:
    """Update an investigation task."""
    async with async_session_maker() as session:
        result = await session.execute(
            select(InvestigationTask).where(InvestigationTask.task_id == task_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            return None

        for key, value in update_data.items():
            if hasattr(task, key):
                setattr(task, key, value)

        await session.commit()
        await session.refresh(task)

        return {
            "id": task.id,
            "task_id": task.task_id,
            "target_user_id": task.target_user_id,
            "trigger_event": task.trigger_event,
            "status": task.status,
            "risk_level": task.risk_level,
            "final_report_json": task.final_report_json,
            "human_approval_needed": task.human_approval_needed,
            "approval_result": task.approval_result,
            "approver_id": task.approver_id,
            "approval_comment": task.approval_comment,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }


async def save_audit_log(log_data: dict) -> AuditLog:
    """Save an audit log entry."""
    async with async_session_maker() as session:
        async with session.begin():
            log = AuditLog(
                trace_id=log_data["trace_id"],
                task_id=log_data["task_id"],
                node_name=log_data["node_name"],
                input_data_json=log_data.get("input_data_json"),
                output_data_json=log_data.get("output_data_json"),
                duration_ms=log_data.get("duration_ms"),
                error=log_data.get("error"),
            )
            session.add(log)
            await session.commit()
            await session.refresh(log)
            return log


async def get_audit_logs_for_task(task_id: str) -> List[dict]:
    """Get all audit logs for a task."""
    async with async_session_maker() as session:
        result = await session.execute(
            select(AuditLog)
            .where(AuditLog.task_id == task_id)
            .order_by(AuditLog.created_at)
        )
        logs = result.scalars().all()
        return [
            {
                "id": log.id,
                "trace_id": log.trace_id,
                "task_id": log.task_id,
                "node_name": log.node_name,
                "input_data_json": log.input_data_json,
                "output_data_json": log.output_data_json,
                "duration_ms": log.duration_ms,
                "error": log.error,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]