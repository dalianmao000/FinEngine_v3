"""Tests for investigation nodes."""

import pytest
from app.investigation.nodes import (
    gather_intel_node,
    graph_explorer_node,
    risk_reasoner_node,
    report_generator_node,
)
from app.graph_rag.cypher_generator import generate_cypher_query


class TestCypherGenerator:
    """Tests for cypher_generator module."""

    def test_generate_cypher_query(self):
        """Test cypher query generation."""
        result = generate_cypher_query("user_123", [])
        assert "user_123" in result
        assert "MATCH" in result
        assert "TRANSFER" in result


class TestGatherIntelNode:
    """Tests for gather_intel_node."""

    @pytest.mark.asyncio
    async def test_gather_intel_node_basic(self):
        """Test gather_intel_node collects evidence."""
        state = {
            "target_user_id": "user_123",
            "trigger_event": "suspicious_login",
        }
        result = await gather_intel_node(state)

        assert "collected_evidence" in result
        evidence = result["collected_evidence"]
        assert "transaction_history" in evidence
        assert "device_info" in evidence
        assert "ip_profile" in evidence
        assert "blacklist_status" in evidence
        assert result["status"] == "GATHERING"

    @pytest.mark.asyncio
    async def test_gather_intel_node_transaction_data(self):
        """Test transaction data is properly collected."""
        state = {"target_user_id": "user_123", "trigger_event": "test"}
        result = await gather_intel_node(state)

        tx_data = result["collected_evidence"]["transaction_history"]
        assert tx_data["user_id"] == "user_123"
        assert "transactions" in tx_data
        assert "total_count" in tx_data

    @pytest.mark.asyncio
    async def test_gather_intel_node_device_info(self):
        """Test device info is properly collected."""
        state = {"target_user_id": "user_123", "trigger_event": "test"}
        result = await gather_intel_node(state)

        device_info = result["collected_evidence"]["device_info"]
        assert device_info["user_id"] == "user_123"
        assert "risk_level" in device_info
        assert device_info["risk_level"] == "HIGH"


class TestGraphExplorerNode:
    """Tests for graph_explorer_node."""

    @pytest.mark.asyncio
    async def test_graph_explorer_node_basic(self):
        """Test graph_explorer_node queries graphs."""
        state = {
            "target_user_id": "user_123",
            "collected_evidence": {
                "transaction_history": {"transactions": []}
            },
        }
        result = await graph_explorer_node(state)

        assert "graph_query_result" in result
        assert "Fund Flow" in result["graph_query_result"]
        assert "Relationship Graph" in result["graph_query_result"]
        assert result["status"] == "GRAPHING"

    @pytest.mark.asyncio
    async def test_graph_explorer_node_contains_cypher(self):
        """Test graph query result contains cypher query."""
        state = {
            "target_user_id": "user_123",
            "collected_evidence": {
                "transaction_history": {"transactions": []}
            },
        }
        result = await graph_explorer_node(state)

        assert "MATCH" in result["graph_query_result"]
        assert "user_123" in result["graph_query_result"]


class TestRiskReasonerNode:
    """Tests for risk_reasoner_node."""

    @pytest.mark.asyncio
    async def test_risk_reasoner_node_high_risk(self):
        """Test risk reasoner with HIGH risk indicators."""
        state = {
            "collected_evidence": {
                "device_info": {"risk_level": "HIGH"},
                "blacklist_status": {"is_blacklisted": True},
            },
            "graph_query_result": "资金回流 detected in analysis",
        }
        result = await risk_reasoner_node(state)

        assert result["risk_level"] == "HIGH"
        assert result["final_report"]["confidence"] == 0.92
        assert result["status"] == "REASONING"
        assert len(result["final_report"]["risk_indicators"]) >= 3

    @pytest.mark.asyncio
    async def test_risk_reasoner_node_medium_risk(self):
        """Test risk reasoner with MEDIUM risk indicators."""
        state = {
            "collected_evidence": {
                "device_info": {"risk_level": "HIGH"},
                "blacklist_status": {"is_blacklisted": False},
            },
            "graph_query_result": "No suspicious patterns",
        }
        result = await risk_reasoner_node(state)

        assert result["risk_level"] == "MEDIUM"
        assert result["final_report"]["confidence"] == 0.65
        assert len(result["final_report"]["risk_indicators"]) == 1

    @pytest.mark.asyncio
    async def test_risk_reasoner_node_low_risk(self):
        """Test risk reasoner with LOW risk indicators."""
        state = {
            "collected_evidence": {
                "device_info": {"risk_level": "LOW"},
                "blacklist_status": {"is_blacklisted": False},
            },
            "graph_query_result": "Normal transaction patterns",
        }
        result = await risk_reasoner_node(state)

        assert result["risk_level"] == "LOW"
        assert result["final_report"]["confidence"] == 0.95
        assert len(result["final_report"]["risk_indicators"]) == 0

    @pytest.mark.asyncio
    async def test_risk_reasoner_node_pyramid_scheme(self):
        """Test risk reasoner detects pyramid scheme indicator."""
        state = {
            "collected_evidence": {
                "device_info": {"risk_level": "LOW"},
                "blacklist_status": {"is_blacklisted": False},
            },
            "graph_query_result": "传销 pattern detected",
        }
        result = await risk_reasoner_node(state)

        assert result["risk_level"] == "MEDIUM"
        assert "传销" in result["final_report"]["risk_indicators"][0]

    @pytest.mark.asyncio
    async def test_risk_reasoner_node_returns_final_report(self):
        """Test risk reasoner returns proper final_report structure."""
        state = {
            "collected_evidence": {
                "device_info": {"risk_level": "MEDIUM"},
                "blacklist_status": {"is_blacklisted": False},
            },
            "graph_query_result": "some pattern",
        }
        result = await risk_reasoner_node(state)

        assert "final_report" in result
        assert "risk_level" in result["final_report"]
        assert "confidence" in result["final_report"]
        assert "risk_indicators" in result["final_report"]


class TestReportGeneratorNode:
    """Tests for report_generator_node."""

    @pytest.mark.asyncio
    async def test_report_generator_node_basic(self):
        """Test report generator creates report."""
        state = {
            "collected_evidence": {
                "transaction_history": {"total_count": 5, "transactions": []},
                "device_info": {"risk_level": "HIGH"},
                "ip_profile": {"risk_score": 85},
                "blacklist_status": {"is_blacklisted": False},
            },
            "graph_query_result": "Fund flow analysis summary",
            "final_report": {
                "risk_level": "HIGH",
                "confidence": 0.92,
                "risk_indicators": ["test"],
                "reasoning_summary": "Test reasoning",
            },
            "risk_level": "HIGH",
        }
        result = await report_generator_node(state)

        assert "final_report" in result
        assert "human_approval_needed" in result
        assert result["human_approval_needed"] is True
        assert result["status"] == "GENERATING"

    @pytest.mark.asyncio
    async def test_report_generator_node_report_id_format(self):
        """Test report ID has correct format."""
        state = {
            "collected_evidence": {},
            "graph_query_result": "",
            "final_report": {"risk_level": "LOW", "confidence": 0.95},
            "risk_level": "LOW",
        }
        result = await report_generator_node(state)

        report_id = result["final_report"]["report_id"]
        assert report_id.startswith("RPT-")
        assert len(report_id) > len("RPT-YYYYMMDD-")

    @pytest.mark.asyncio
    async def test_report_generator_node_evidence_list(self):
        """Test evidence list is properly built."""
        state = {
            "collected_evidence": {
                "transaction_history": {"total_count": 3},
                "device_info": {"risk_level": "HIGH"},
            },
            "graph_query_result": "test graph result",
            "final_report": {"risk_level": "LOW", "confidence": 0.95},
            "risk_level": "LOW",
        }
        result = await report_generator_node(state)

        evidence_list = result["final_report"]["evidence_list"]
        assert len(evidence_list) > 0

    @pytest.mark.asyncio
    async def test_report_generator_node_high_risk_needs_approval(self):
        """Test HIGH risk level requires human approval."""
        state = {
            "collected_evidence": {},
            "graph_query_result": "",
            "final_report": {"risk_level": "HIGH", "confidence": 0.92},
            "risk_level": "HIGH",
        }
        result = await report_generator_node(state)

        assert result["human_approval_needed"] is True

    @pytest.mark.asyncio
    async def test_report_generator_node_low_risk_no_approval(self):
        """Test LOW risk level does not require human approval."""
        state = {
            "collected_evidence": {},
            "graph_query_result": "",
            "final_report": {"risk_level": "LOW", "confidence": 0.95},
            "risk_level": "LOW",
        }
        result = await report_generator_node(state)

        assert result["human_approval_needed"] is False

    @pytest.mark.asyncio
    async def test_report_generator_node_suggested_action(self):
        """Test suggested action is properly set."""
        state = {
            "collected_evidence": {},
            "graph_query_result": "",
            "final_report": {"risk_level": "HIGH", "confidence": 0.92},
            "risk_level": "HIGH",
        }
        result = await report_generator_node(state)

        assert result["final_report"]["suggested_action"] == "freeze_account"