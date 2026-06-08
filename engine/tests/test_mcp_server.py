"""Tests for the MCP server tool layer.

The tool *logic* is tested directly (no SDK needed, so these run in CI). The
FastMCP wiring is exercised only when the optional `mcp` package is installed.
"""

from __future__ import annotations

import pytest

from engine import mcp_server

_HEART = dict(
    history="moderately_suspicious", ecg="normal", age_years=58,
    hypertension=True, hypercholesterolemia=True, diabetes_mellitus=False,
    current_or_recent_smoking=False, family_history_of_cad=False,
    obesity_bmi_over_30=False, history_of_atherosclerotic_disease=False,
    troponin="at_or_below_normal_limit",
)


class TestToolLogic:
    def test_list_conditions(self) -> None:
        items = mcp_server.list_conditions()
        assert any(c["key"] == "heart" for c in items)

    def test_list_presentations(self) -> None:
        assert "chest pain" in mcp_server.list_presentations()

    def test_get_condition_schema(self) -> None:
        schema = mcp_server.get_condition_schema("heart")
        assert schema["type"] == "object" and schema["properties"]

    def test_describe_condition(self) -> None:
        d = mcp_server.describe_condition("heart")
        assert d["key"] == "heart" and "input_schema" in d

    def test_run_algorithm_success(self) -> None:
        out = mcp_server.run_algorithm("heart", _HEART)
        assert out["ok"] is True
        assert out["result"]["score"] == 3
        assert "not a medical device" in out["disclaimer"].lower()

    def test_run_algorithm_missing_inputs(self) -> None:
        out = mcp_server.run_algorithm("kdigo", {"egfr_ml_min_1_73m2": 50.0})
        assert out["ok"] is False
        assert "acr_mg_per_mmol" in out["missing_inputs"]

    def test_run_algorithm_unknown_condition(self) -> None:
        out = mcp_server.run_algorithm("nope", {})
        assert out["ok"] is False
        assert "unknown condition" in out["error"]

    def test_run_algorithm_out_of_range(self) -> None:
        out = mcp_server.run_algorithm("kdigo", {
            "egfr_ml_min_1_73m2": -1.0, "acr_mg_per_mmol": 1.0,
            "persistent_over_3_months": True,
        })
        assert out["ok"] is False
        assert "negative" in out["error"]

    def test_suggest_algorithms(self) -> None:
        records = mcp_server.suggest_algorithms(_HEART, presentation="chest pain")
        heart = next(r for r in records if r["key"] == "heart")
        assert heart["runnable"] is True

    def test_run_applicable(self) -> None:
        out = mcp_server.run_applicable(_HEART, presentation="chest pain")
        assert any(r["key"] == "heart" for r in out["applicable"])
        assert "disclaimer" in out


class TestServerWiring:
    """Exercised only when the optional MCP SDK is installed."""

    def test_build_server_registers_all_tools(self) -> None:
        pytest.importorskip("mcp")
        import asyncio

        server = mcp_server.build_server()
        tools = asyncio.run(server.list_tools())
        names = {t.name for t in tools}
        assert names == {
            "list_conditions", "list_presentations", "get_condition_schema",
            "describe_condition", "run_algorithm", "suggest_algorithms",
            "run_applicable",
        }
        # Every tool carries a description (the agent reads these) and a schema.
        for tool in tools:
            assert tool.description and tool.description.strip()
            assert tool.inputSchema["type"] == "object"
