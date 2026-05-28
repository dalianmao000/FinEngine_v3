"""Tests for Human-in-the-loop approval workflow."""

import pytest
from app.safety.human_in_loop import HumanInLoopManager, require_human_approval


@pytest.fixture
def manager():
    """Create a fresh HumanInLoopManager for each test."""
    return HumanInLoopManager(approval_timeout_hours=2)


class TestHumanInLoopManager:
    """Tests for HumanInLoopManager class."""

    def test_create_approval_task(self, manager):
        """Test creating an approval task."""
        report = {"user_id": "user_123", "risk_level": "HIGH"}
        task = manager.create_approval_task("task_001", report)

        assert task["task_id"] == "task_001"
        assert task["status"] == "PENDING"
        assert task["report"] == report
        assert task["approver_id"] is None
        assert task["comment"] is None
        assert task["approved_at"] is None
        assert task["rejected_at"] is None

    def test_create_approval_task_with_callback(self, manager):
        """Test creating task with callback URL."""
        report = {"user_id": "user_123"}
        callback_url = "https://example.com/callback"
        task = manager.create_approval_task("task_002", report, callback_url)

        assert task["callback_url"] == callback_url

    def test_get_approval_status(self, manager):
        """Test getting approval status."""
        report = {"user_id": "user_123"}
        manager.create_approval_task("task_001", report)

        status = manager.get_approval_status("task_001")
        assert status is not None
        assert status["task_id"] == "task_001"
        assert status["status"] == "PENDING"

    def test_get_approval_status_not_found(self, manager):
        """Test getting status for non-existent task."""
        status = manager.get_approval_status("nonexistent")
        assert status is None

    def test_approve(self, manager):
        """Test approving a task."""
        report = {"user_id": "user_123"}
        manager.create_approval_task("task_001", report)

        result = manager.approve("task_001", "approver_001", "Approved - risk verified")
        assert result is True

        status = manager.get_approval_status("task_001")
        assert status["status"] == "APPROVED"
        assert status["approver_id"] == "approver_001"
        assert status["comment"] == "Approved - risk verified"
        assert status["approved_at"] is not None

    def test_approve_not_found(self, manager):
        """Test approving non-existent task."""
        result = manager.approve("nonexistent", "approver_001", "comment")
        assert result is False

    def test_reject(self, manager):
        """Test rejecting a task."""
        report = {"user_id": "user_123"}
        manager.create_approval_task("task_001", report)

        result = manager.reject("task_001", "approver_001", "Rejected - insufficient evidence")
        assert result is True

        status = manager.get_approval_status("task_001")
        assert status["status"] == "REJECTED"
        assert status["approver_id"] == "approver_001"
        assert status["comment"] == "Rejected - insufficient evidence"
        assert status["rejected_at"] is not None

    def test_reject_not_found(self, manager):
        """Test rejecting non-existent task."""
        result = manager.reject("nonexistent", "approver_001", "comment")
        assert result is False

    def test_timeout_hours_config(self, manager):
        """Test timeout configuration."""
        assert manager.approval_timeout_hours == 2

    def test_multiple_tasks(self, manager):
        """Test managing multiple approval tasks."""
        report1 = {"user_id": "user_1"}
        report2 = {"user_id": "user_2"}
        report3 = {"user_id": "user_3"}

        manager.create_approval_task("task_1", report1)
        manager.create_approval_task("task_2", report2)
        manager.create_approval_task("task_3", report3)

        manager.approve("task_1", "approver_1", "ok")
        manager.reject("task_2", "approver_2", "not ok")

        assert manager.get_approval_status("task_1")["status"] == "APPROVED"
        assert manager.get_approval_status("task_2")["status"] == "REJECTED"
        assert manager.get_approval_status("task_3")["status"] == "PENDING"


@pytest.mark.asyncio
async def test_require_human_approval():
    """Test require_human_approval helper function."""
    report = {"user_id": "user_123", "risk_level": "HIGH"}
    result = await require_human_approval("task_001", report)
    assert result is True