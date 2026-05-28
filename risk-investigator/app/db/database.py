from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON, func, select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, InvestigationTask, AuditLog

# Valid column names for InvestigationTask - used for validation in updates
INVESTIGATION_TASK_COLUMNS = frozenset([
    "status", "risk_level", "final_report_json", "human_approval_needed",
    "approval_result", "approver_id", "approval_comment", "completed_at"
])

# Module-level engine and session maker - initialized once via init_db()
engine: Optional[create_async_engine] = None
async_session_maker: Optional[async_sessionmaker] = None


async def init_db(database_url: str) -> None:
    """Initialize the database engine and create all tables."""
    global engine, async_session_maker
    engine = create_async_engine(database_url, echo=False, future=True)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def _task_to_dict(task: InvestigationTask) -> dict:
    """Convert an InvestigationTask model instance to a dictionary."""
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
        try:
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
        except Exception as e:
            await session.rollback()
            raise RuntimeError(f"Failed to save investigation task: {e}") from e


async def get_investigation_task(task_id: str) -> Optional[dict]:
    """Get an investigation task by task_id."""
    async with async_session_maker() as session:
        try:
            result = await session.execute(
                select(InvestigationTask).where(InvestigationTask.task_id == task_id)
            )
            task = result.scalar_one_or_none()
            if task:
                return _task_to_dict(task)
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to get investigation task: {e}") from e


async def update_investigation_task(task_id: str, update_data: dict) -> Optional[dict]:
    """Update an investigation task."""
    async with async_session_maker() as session:
        try:
            result = await session.execute(
                select(InvestigationTask).where(InvestigationTask.task_id == task_id)
            )
            task = result.scalar_one_or_none()
            if not task:
                return None

            for key, value in update_data.items():
                if key in INVESTIGATION_TASK_COLUMNS and hasattr(task, key):
                    setattr(task, key, value)

            await session.commit()
            await session.refresh(task)

            return _task_to_dict(task)
        except Exception as e:
            await session.rollback()
            raise RuntimeError(f"Failed to update investigation task: {e}") from e


async def save_audit_log(log_data: dict) -> AuditLog:
    """Save an audit log entry."""
    async with async_session_maker() as session:
        try:
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
        except Exception as e:
            await session.rollback()
            raise RuntimeError(f"Failed to save audit log: {e}") from e


async def get_audit_logs_for_task(task_id: str) -> List[dict]:
    """Get all audit logs for a task."""
    async with async_session_maker() as session:
        try:
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
        except Exception as e:
            raise RuntimeError(f"Failed to get audit logs: {e}") from e