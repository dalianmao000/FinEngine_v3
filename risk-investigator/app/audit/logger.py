import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from app.db.database import save_audit_log


class AuditLogger:
    def __init__(self):
        self._trace_id: Optional[str] = None

    def start_trace(self) -> str:
        """Start a new trace and return trace_id"""
        self._trace_id = f"TRACE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:12].upper()}"
        return self._trace_id

    def get_trace_id(self) -> str:
        """Get current trace_id, or start a new one if not set"""
        if not self._trace_id:
            return self.start_trace()
        return self._trace_id

    async def log_node(
        self,
        task_id: str,
        node_name: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        error: Optional[str] = None,
    ):
        """Log a node execution to the database"""
        log_data = {
            "id": str(uuid.uuid4()),
            "trace_id": self.get_trace_id(),
            "task_id": task_id,
            "node_name": node_name,
            "input_data_json": input_data,
            "output_data_json": output_data,
            "duration_ms": duration_ms,
            "error": error,
        }
        await save_audit_log(log_data)


audit_logger = AuditLogger()