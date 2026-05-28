from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class InvestigationTask(Base):
    __tablename__ = "investigation_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    target_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    trigger_event: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    final_report_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    human_approval_needed: Mapped[bool] = mapped_column(Boolean, default=False)
    approval_result: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    approver_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approval_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trace_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    node_name: Mapped[str] = mapped_column(String(100), nullable=False)
    input_data_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    output_data_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())