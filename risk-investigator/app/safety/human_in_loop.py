"""Human-in-the-loop approval workflow management."""

from datetime import datetime, timezone
from typing import Dict, Optional
import uuid


class HumanInLoopManager:
    """Manager for human-in-the-loop approval workflows."""

    def __init__(self, approval_timeout_hours: int = 2):
        """
        Initialize the HumanInLoopManager.

        Args:
            approval_timeout_hours: Timeout for approval tasks in hours.
        """
        self.approval_timeout_hours = approval_timeout_hours
        self._pending_approvals: dict = {}

    def _utc_now(self) -> str:
        """Return current UTC time as ISO format string."""
        return datetime.now(timezone.utc).isoformat()

    def create_approval_task(
        self,
        task_id: str,
        report: dict,
        callback_url: Optional[str] = None,
    ) -> dict:
        """
        Create a new approval task.

        Args:
            task_id: Unique identifier for the task
            report: The investigation report requiring approval
            callback_url: Optional callback URL for notifications

        Returns:
            Task dict with status PENDING
        """
        task = {
            "task_id": task_id,
            "status": "PENDING",
            "report": report,
            "callback_url": callback_url,
            "created_at": self._utc_now(),
            "updated_at": self._utc_now(),
            "approver_id": None,
            "comment": None,
            "approved_at": None,
            "rejected_at": None,
        }
        self._pending_approvals[task_id] = task
        return task

    def get_approval_status(self, task_id: str) -> Optional[dict]:
        """
        Get the status of a pending approval task.

        Args:
            task_id: The task ID to look up

        Returns:
            Task dict if found, None otherwise
        """
        return self._pending_approvals.get(task_id)

    def approve(
        self,
        task_id: str,
        approver_id: str,
        comment: str,
    ) -> bool:
        """
        Approve a pending task.

        Args:
            task_id: The task ID to approve
            approver_id: ID of the approver
            comment: Approval comment

        Returns:
            True if approved successfully, False if task not found
        """
        task = self._pending_approvals.get(task_id)
        if not task:
            return False

        task["status"] = "APPROVED"
        task["approver_id"] = approver_id
        task["comment"] = comment
        task["approved_at"] = self._utc_now()
        task["updated_at"] = self._utc_now()
        return True

    def reject(
        self,
        task_id: str,
        approver_id: str,
        comment: str,
    ) -> bool:
        """
        Reject a pending task.

        Args:
            task_id: The task ID to reject
            approver_id: ID of the rejector
            comment: Rejection reason

        Returns:
            True if rejected successfully, False if task not found
        """
        task = self._pending_approvals.get(task_id)
        if not task:
            return False

        task["status"] = "REJECTED"
        task["approver_id"] = approver_id
        task["comment"] = comment
        task["rejected_at"] = self._utc_now()
        task["updated_at"] = self._utc_now()
        return True


# Global instance
human_in_loop_manager = HumanInLoopManager()


async def require_human_approval(task_id: str, report: dict) -> bool:
    """
    Create a human approval task for a high-risk investigation.

    Args:
        task_id: Unique identifier for the task
        report: The investigation report

    Returns:
        True (always, caller should await approval separately)
    """
    human_in_loop_manager.create_approval_task(task_id, report)
    return True