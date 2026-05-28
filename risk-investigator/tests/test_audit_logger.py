import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.audit.logger import AuditLogger, audit_logger


class TestAuditLogger:
    """Tests for AuditLogger class"""

    def test_start_trace_generates_trace_id(self):
        """Test that start_trace generates a properly formatted trace_id"""
        logger = AuditLogger()
        trace_id = logger.start_trace()

        assert trace_id is not None
        assert trace_id.startswith("TRACE-")
        assert len(trace_id) > 20

    def test_start_trace_sets_trace_id(self):
        """Test that start_trace sets the internal trace_id"""
        logger = AuditLogger()
        trace_id = logger.start_trace()

        assert logger._trace_id == trace_id

    def test_get_trace_id_when_set(self):
        """Test that get_trace_id returns existing trace_id"""
        logger = AuditLogger()
        trace_id = logger.start_trace()

        assert logger.get_trace_id() == trace_id

    def test_get_trace_id_when_not_set(self):
        """Test that get_trace_id starts new trace if not set"""
        logger = AuditLogger()
        trace_id = logger.get_trace_id()

        assert trace_id is not None
        assert trace_id.startswith("TRACE-")
        assert logger._trace_id is not None

    def test_trace_id_format_includes_date(self):
        """Test that trace_id includes date in YYYYMMDD format"""
        from datetime import datetime
        logger = AuditLogger()
        trace_id = logger.start_trace()

        expected_date = datetime.now().strftime('%Y%m%d')
        assert expected_date in trace_id

    def test_trace_id_format_includes_uuid(self):
        """Test that trace_id includes uppercase hex UUID segment"""
        logger = AuditLogger()
        trace_id = logger.start_trace()
        parts = trace_id.split("-")

        assert len(parts) == 3
        assert parts[0] == "TRACE"
        assert len(parts[2]) == 12
        assert parts[2].isupper()

    def test_audit_logger_singleton_exists(self):
        """Test that module-level audit_logger instance exists"""
        assert audit_logger is not None
        assert isinstance(audit_logger, AuditLogger)

    @pytest.mark.asyncio
    async def test_log_node_calls_save_audit_log(self):
        """Test that log_node calls save_audit_log with correct data"""
        logger = AuditLogger()
        logger.start_trace()

        mock_log_data = {}

        async def mock_save(log_data):
            mock_log_data.update(log_data)
            return MagicMock()

        with patch("app.audit.logger.save_audit_log", side_effect=mock_save):
            await logger.log_node(
                task_id="task-123",
                node_name="test_node",
                input_data={"key": "value"},
                output_data={"result": "ok"},
                duration_ms=100,
                error=None,
            )

        assert mock_log_data["trace_id"] == logger._trace_id
        assert mock_log_data["task_id"] == "task-123"
        assert mock_log_data["node_name"] == "test_node"
        assert mock_log_data["input_data_json"] == {"key": "value"}
        assert mock_log_data["output_data_json"] == {"result": "ok"}
        assert mock_log_data["duration_ms"] == 100
        assert mock_log_data["error"] is None

    @pytest.mark.asyncio
    async def test_log_node_with_error(self):
        """Test that log_node properly handles error field"""
        logger = AuditLogger()
        logger.start_trace()

        mock_log_data = {}

        async def mock_save(log_data):
            mock_log_data.update(log_data)
            return MagicMock()

        with patch("app.audit.logger.save_audit_log", side_effect=mock_save):
            await logger.log_node(
                task_id="task-456",
                node_name="failing_node",
                error="Something went wrong",
            )

        assert mock_log_data["error"] == "Something went wrong"

    @pytest.mark.asyncio
    async def test_log_node_without_optional_fields(self):
        """Test that log_node works with only required fields"""
        logger = AuditLogger()
        logger.start_trace()

        mock_log_data = {}

        async def mock_save(log_data):
            mock_log_data.update(log_data)
            return MagicMock()

        with patch("app.audit.logger.save_audit_log", side_effect=mock_save):
            await logger.log_node(
                task_id="task-789",
                node_name="minimal_node",
            )

        assert mock_log_data["task_id"] == "task-789"
        assert mock_log_data["node_name"] == "minimal_node"
        assert mock_log_data["input_data_json"] is None
        assert mock_log_data["output_data_json"] is None
        assert mock_log_data["duration_ms"] is None

    @pytest.mark.asyncio
    async def test_log_node_auto_starts_trace(self):
        """Test that log_node starts a trace if none is set"""
        logger = AuditLogger()

        mock_log_data = {}

        async def mock_save(log_data):
            mock_log_data.update(log_data)
            return MagicMock()

        with patch("app.audit.logger.save_audit_log", side_effect=mock_save):
            await logger.log_node(
                task_id="task-auto",
                node_name="auto_node",
            )

        assert logger._trace_id is not None
        assert mock_log_data["trace_id"] is not None
        assert mock_log_data["trace_id"].startswith("TRACE-")