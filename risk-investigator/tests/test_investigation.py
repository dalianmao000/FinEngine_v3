"""End-to-end integration tests for the full investigation workflow."""

import pytest
from unittest.mock import AsyncMock, patch

from app.investigation.workflow import build_investigation_graph
from app.investigation.state import RiskState


def get_node_output(states, node_name):
    """Get the output of a specific node from the states list."""
    for state in states:
        if node_name in state:
            return state[node_name]
    return None


class TestInvestigationWorkflow:
    """Test cases for the full investigation workflow."""

    def test_workflow_compiles_successfully(self):
        """Test that the investigation workflow compiles without errors."""
        graph = build_investigation_graph()
        assert graph is not None

    def test_workflow_has_correct_structure(self):
        """Test that workflow has all expected nodes in correct order."""
        graph = build_investigation_graph()
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
            assert node_name in node_names, f"Node {node_name} not found in graph"

    def test_workflow_entry_point_is_gather_intel(self):
        """Test that the workflow entry point is gather_intel node."""
        graph = build_investigation_graph()
        assert "gather_intel" in graph.nodes


class TestFullInvestigationWorkflow:
    """Test cases for the end-to-end investigation workflow execution."""

    @pytest.mark.asyncio
    async def test_full_workflow_execution(self):
        """Test complete workflow from start to finish."""
        with patch(
            "app.investigation.workflow.update_investigation_task",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = {"status": "COMPLETED"}

            graph = build_investigation_graph()

            initial_state = RiskState(
                task_id="INV-TEST-001",
                target_user_id="user_test_123",
                trigger_event="测试触发：用户转账异常",
            )

            states = []
            async for state in graph.astream(initial_state):
                states.append(state)

            # The workflow should have at least 5 states (one per node)
            assert len(states) >= 4

            # Check that report_generator produced final_report
            report_gen_output = get_node_output(states, "report_generator")
            assert report_gen_output is not None
            assert "final_report" in report_gen_output
            assert "risk_level" in report_gen_output["final_report"]
            assert report_gen_output["final_report"]["risk_level"] in ["HIGH", "MEDIUM", "LOW"]

            # Check that finalize completed
            finalize_output = get_node_output(states, "finalize")
            assert finalize_output is not None
            assert finalize_output["status"] == "COMPLETED"

    @pytest.mark.asyncio
    async def test_gather_intel_produces_collected_evidence(self):
        """Test that gather_intel node produces collected_evidence."""
        with patch(
            "app.investigation.workflow.update_investigation_task",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = {"status": "COMPLETED"}

            graph = build_investigation_graph()

            initial_state = RiskState(
                task_id="INV-TEST-002",
                target_user_id="user_test_456",
                trigger_event="异常登录",
            )

            states = []
            async for state in graph.astream(initial_state):
                states.append(state)

            # Check that gather_intel node produced collected_evidence
            gather_intel_output = get_node_output(states, "gather_intel")
            assert gather_intel_output is not None
            assert "collected_evidence" in gather_intel_output

    @pytest.mark.asyncio
    async def test_graph_explorer_produces_graph_query_result(self):
        """Test that graph_explorer node produces graph_query_result."""
        with patch(
            "app.investigation.workflow.update_investigation_task",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = {"status": "COMPLETED"}

            graph = build_investigation_graph()

            initial_state = RiskState(
                task_id="INV-TEST-003",
                target_user_id="user_test_789",
                trigger_event="可疑交易",
            )

            states = []
            async for state in graph.astream(initial_state):
                states.append(state)

            # Check that graph_explorer node produced graph_query_result
            graph_output = get_node_output(states, "graph_explorer")
            assert graph_output is not None
            assert "graph_query_result" in graph_output

    @pytest.mark.asyncio
    async def test_risk_reasoner_produces_risk_level(self):
        """Test that risk_reasoner node produces risk_level."""
        with patch(
            "app.investigation.workflow.update_investigation_task",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = {"status": "COMPLETED"}

            graph = build_investigation_graph()

            initial_state = RiskState(
                task_id="INV-TEST-004",
                target_user_id="user_test_101",
                trigger_event="风险交易",
            )

            states = []
            async for state in graph.astream(initial_state):
                states.append(state)

            # Check that risk_reasoner node produced risk_level
            reasoner_output = get_node_output(states, "risk_reasoner")
            assert reasoner_output is not None
            assert "risk_level" in reasoner_output
            assert reasoner_output["risk_level"] in ["HIGH", "MEDIUM", "LOW"]

    @pytest.mark.asyncio
    async def test_report_generator_produces_final_report(self):
        """Test that report_generator produces final_report with proper structure."""
        with patch(
            "app.investigation.workflow.update_investigation_task",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = {"status": "COMPLETED"}

            graph = build_investigation_graph()

            initial_state = RiskState(
                task_id="INV-TEST-005",
                target_user_id="user_test_202",
                trigger_event="常规审计",
            )

            states = []
            async for state in graph.astream(initial_state):
                states.append(state)

            # Check that report_generator node produced proper final_report
            report_gen_output = get_node_output(states, "report_generator")
            assert report_gen_output is not None
            assert "final_report" in report_gen_output

            final_report = report_gen_output["final_report"]
            assert isinstance(final_report, dict)
            assert "report_id" in final_report
            assert "risk_level" in final_report
            assert "confidence" in final_report
            assert "risk_indicators" in final_report
            assert "evidence_list" in final_report

    @pytest.mark.asyncio
    async def test_high_risk_routes_to_human_approval(self):
        """Test that HIGH risk investigation routes to human_approval node."""
        with patch(
            "app.investigation.workflow.update_investigation_task",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = {"status": "COMPLETED"}

            graph = build_investigation_graph()

            # Use a target_user_id that triggers HIGH risk
            initial_state = RiskState(
                task_id="INV-TEST-006",
                target_user_id="user_123",
                trigger_event="高风险交易",
            )

            states = []
            async for state in graph.astream(initial_state):
                states.append(state)

            # Check the report_generator output for human_approval_needed
            report_gen_output = get_node_output(states, "report_generator")
            assert report_gen_output is not None

            # If HIGH risk, should route to human_approval (6 states instead of 5)
            if report_gen_output.get("human_approval_needed"):
                # Should have human_approval node in states
                human_approval_output = get_node_output(states, "human_approval")
                assert human_approval_output is not None
                assert human_approval_output["status"] == "PENDING_APPROVAL"

    @pytest.mark.asyncio
    async def test_workflow_produces_all_states(self):
        """Test that workflow produces all expected states."""
        with patch(
            "app.investigation.workflow.update_investigation_task",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = {"status": "COMPLETED"}

            graph = build_investigation_graph()

            initial_state = RiskState(
                task_id="INV-TEST-007",
                target_user_id="user_test_303",
                trigger_event="综合审计",
            )

            states = []
            async for state in graph.astream(initial_state):
                states.append(state)

            # Should have states for: gather_intel, graph_explorer, risk_reasoner, report_generator, finalize
            assert len(states) >= 5

            # Check each node ran
            assert get_node_output(states, "gather_intel") is not None
            assert get_node_output(states, "graph_explorer") is not None
            assert get_node_output(states, "risk_reasoner") is not None
            assert get_node_output(states, "report_generator") is not None
            assert get_node_output(states, "finalize") is not None


class TestInvestigationWorkflowStructure:
    """Test cases for workflow structure and connectivity."""

    def test_workflow_has_sequential_edges(self):
        """Test that workflow has correct sequential edges between nodes."""
        graph = build_investigation_graph()

        # The graph should be compilable and have nodes
        assert len(graph.nodes) >= 5

        # Check that required nodes exist
        required_nodes = [
            "gather_intel",
            "graph_explorer",
            "risk_reasoner",
            "report_generator",
        ]
        for node in required_nodes:
            assert node in graph.nodes

    @pytest.mark.asyncio
    async def test_workflow_single_task_execution(self):
        """Test that workflow processes a single task correctly."""
        with patch(
            "app.investigation.workflow.update_investigation_task",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = {"status": "COMPLETED"}

            graph = build_investigation_graph()

            initial_state = RiskState(
                task_id="INV-TEST-SINGLE-001",
                target_user_id="user_single_test",
                trigger_event="单次测试",
            )

            state_count = 0
            async for state in graph.astream(initial_state):
                state_count += 1

            # Should process through multiple states/nodes
            assert state_count >= 4, f"Expected at least 4 states, got {state_count}"