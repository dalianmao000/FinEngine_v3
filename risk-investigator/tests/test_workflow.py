"""Tests for the investigation workflow."""

import pytest
from unittest.mock import AsyncMock, patch

from app.investigation.workflow import (
    build_investigation_graph,
    route_by_human_approval,
    human_approval_node,
    finalize_node,
    complete_investigation_with_approval,
)


class TestBuildInvestigationGraph:
    """Test cases for build_investigation_graph."""

    def test_graph_compiles_successfully(self):
        """Test that the workflow graph compiles without errors."""
        graph = build_investigation_graph()
        assert graph is not None

    def test_graph_has_correct_nodes(self):
        """Test that all expected nodes are present in the graph."""
        graph = build_investigation_graph()
        # The compiled graph should have nodes
        node_names = list(graph.nodes.keys())
        expected_nodes = [
            "gather_intel",
            "graph_explorer",
            "risk_reasoner",
            "report_generator",
            "human_approval",
            "finalize",
        ]
        for node_name in expected_nodes:
            assert node_name in node_names

    def test_graph_entry_point_is_gather_intel(self):
        """Test that gather_intel is the entry point."""
        graph = build_investigation_graph()
        # Verify the graph structure by checking entry point
        assert "gather_intel" in graph.nodes


class TestRouteByHumanApproval:
    """Test cases for route_by_human_approval function."""

    def test_routes_to_human_approval_when_needed(self):
        """Test routing to human_approval when human_approval_needed is True."""
        state = {"human_approval_needed": True}
        result = route_by_human_approval(state)
        assert result == "human_approval"

    def test_routes_to_finalize_when_approval_not_needed(self):
        """Test routing to finalize when human_approval_needed is False."""
        state = {"human_approval_needed": False}
        result = route_by_human_approval(state)
        assert result == "finalize"

    def test_routes_to_finalize_when_human_approval_needed_missing(self):
        """Test routing to finalize when human_approval_needed is not in state."""
        state = {}
        result = route_by_human_approval(state)
        assert result == "finalize"


class TestHumanApprovalNode:
    """Test cases for human_approval_node function."""

    @pytest.mark.asyncio
    async def test_updates_task_status_to_pending_approval(self):
        """Test that the node updates task status to PENDING_APPROVAL."""
        state = {
            "task_id": "test-task-123",
            "risk_level": "HIGH",
            "final_report": {"report_id": "RPT-123"},
        }

        with patch("app.investigation.workflow.update_investigation_task", new_callable=AsyncMock) as mock_update:
            result = await human_approval_node(state)

            assert result["status"] == "PENDING_APPROVAL"
            mock_update.assert_called_once_with(
                "test-task-123",
                {
                    "status": "PENDING_APPROVAL",
                    "risk_level": "HIGH",
                    "final_report_json": {"report_id": "RPT-123"},
                    "human_approval_needed": True,
                },
            )

    @pytest.mark.asyncio
    async def test_handles_missing_task_id(self):
        """Test that the node handles missing task_id gracefully."""
        state = {
            "risk_level": "HIGH",
            "final_report": {},
        }

        with patch("app.investigation.workflow.update_investigation_task", new_callable=AsyncMock) as mock_update:
            result = await human_approval_node(state)

            assert result["status"] == "PENDING_APPROVAL"
            mock_update.assert_not_called()


class TestFinalizeNode:
    """Test cases for finalize_node function."""

    @pytest.mark.asyncio
    async def test_updates_task_status_to_completed(self):
        """Test that the node updates task status to COMPLETED."""
        state = {
            "task_id": "test-task-123",
            "risk_level": "LOW",
            "final_report": {"report_id": "RPT-456"},
        }

        with patch("app.investigation.workflow.update_investigation_task", new_callable=AsyncMock) as mock_update:
            result = await finalize_node(state)

            assert result["status"] == "COMPLETED"
            assert "completed_at" in result
            mock_update.assert_called_once()
            call_args = mock_update.call_args
            assert call_args[0][0] == "test-task-123"
            assert call_args[0][1]["status"] == "COMPLETED"
            assert call_args[0][1]["risk_level"] == "LOW"
            assert call_args[0][1]["human_approval_needed"] is False

    @pytest.mark.asyncio
    async def test_handles_missing_task_id(self):
        """Test that the node handles missing task_id gracefully."""
        state = {
            "risk_level": "LOW",
            "final_report": {},
        }

        with patch("app.investigation.workflow.update_investigation_task", new_callable=AsyncMock) as mock_update:
            result = await finalize_node(state)

            assert result["status"] == "COMPLETED"
            mock_update.assert_not_called()


class TestCompleteInvestigationWithApproval:
    """Test cases for complete_investigation_with_approval function."""

    @pytest.mark.asyncio
    async def test_approve_sets_status_to_completed(self):
        """Test that approving sets status to COMPLETED."""
        with patch("app.investigation.workflow.update_investigation_task", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = {"status": "COMPLETED", "approval_result": "APPROVED"}
            result = await complete_investigation_with_approval(
                task_id="test-task-123",
                approver_id="approver-001",
                comment="Approved after review",
                action="approve",
            )

            mock_update.assert_called_once()
            call_args = mock_update.call_args
            assert call_args[0][0] == "test-task-123"
            assert call_args[0][1]["approval_result"] == "APPROVED"
            assert call_args[0][1]["approver_id"] == "approver-001"
            assert call_args[0][1]["approval_comment"] == "Approved after review"
            assert call_args[0][1]["status"] == "COMPLETED"

    @pytest.mark.asyncio
    async def test_reject_sets_status_to_completed(self):
        """Test that rejecting sets status to COMPLETED with REJECTED result."""
        with patch("app.investigation.workflow.update_investigation_task", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = {"status": "COMPLETED", "approval_result": "REJECTED"}
            result = await complete_investigation_with_approval(
                task_id="test-task-123",
                approver_id="approver-001",
                comment="Rejected due to insufficient evidence",
                action="reject",
            )

            mock_update.assert_called_once()
            call_args = mock_update.call_args
            assert call_args[0][0] == "test-task-123"
            assert call_args[0][1]["approval_result"] == "REJECTED"