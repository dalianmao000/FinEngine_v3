import json
import uuid
from datetime import datetime
from typing import Optional


class TraceLogger:
    """全链路TraceLogger"""

    def __init__(self, session=None):
        self.session = session
        self._buffer = []
        self._buffer_size = 10

    async def log_node(
        self,
        trace_id: str,
        node: str,
        data: dict,
    ):
        """记录单个节点"""
        record = {
            "id": str(uuid.uuid4()),
            "trace_id": trace_id,
            "node": node,
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": data.get("duration_ms", 0),
            "error": data.get("error"),
            "metadata": data.get("metadata", {}),
        }

        self._buffer.append(record)

        if len(self._buffer) >= self._buffer_size:
            await self._flush()

    async def log_full_trace(
        self,
        trace_id: str,
        user_id: str,
        scenario: str,
        input_text: str,
        output_text: str,
        blocked: bool,
        safety_events: list,
        total_duration_ms: int,
    ):
        """记录完整链路"""
        record = {
            "id": str(uuid.uuid4()),
            "trace_id": trace_id,
            "user_id": user_id,
            "scenario": scenario,
            "input_text": input_text,
            "output_text": output_text,
            "blocked": blocked,
            "block_reason": json.dumps(safety_events),
            "nodes_json": json.dumps(self._buffer),
            "total_duration_ms": total_duration_ms,
            "created_at": datetime.utcnow().isoformat(),
        }

        if self.session:
            from app.database import AuditLog
            log_entry = AuditLog(**record)
            self.session.add(log_entry)
            await self.session.commit()

    async def _flush(self):
        """批量写入"""
        self._buffer.clear()

    async def get_trace(self, trace_id: str) -> list[dict]:
        """获取链路记录"""
        return [r for r in self._buffer if r["trace_id"] == trace_id]
