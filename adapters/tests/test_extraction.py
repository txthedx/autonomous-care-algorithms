"""Tests for the extraction adapter.

The orchestration and the Claude extractor are tested with deterministic /
fake objects — no network, no API key, and no `anthropic` install required.
"""

from __future__ import annotations

from typing import Any

from adapters.extraction import (
    ClaudeExtractor,
    DictExtractor,
    assess_note,
    union_schema,
)

_HEART = dict(
    history="moderately_suspicious", ecg="normal", age_years=58,
    hypertension=True, hypercholesterolemia=True, diabetes_mellitus=False,
    current_or_recent_smoking=False, family_history_of_cad=False,
    obesity_bmi_over_30=False, history_of_atherosclerotic_disease=False,
    troponin="at_or_below_normal_limit",
)


class TestUnionSchema:
    def test_merges_properties(self) -> None:
        schema = union_schema(["heart", "kdigo"])
        assert "history" in schema["properties"]          # from HEART
        assert "egfr_ml_min_1_73m2" in schema["properties"]  # from KDIGO
        assert schema["required"] == []

    def test_shared_field_name_merges_once(self) -> None:
        # age_years appears in several conditions; it should resolve to one prop.
        schema = union_schema(["heart", "crb_65", "cha2ds2_vasc"])
        assert schema["properties"]["age_years"] == {"type": "integer"}


class TestDictExtractor:
    def test_filters_to_schema(self) -> None:
        extractor = DictExtractor({**_HEART, "irrelevant": 1})
        schema = union_schema(["heart"])
        out = extractor(_NOTE, schema)
        assert "irrelevant" not in out
        assert out["history"] == "moderately_suspicious"


_NOTE = "58yo with chest pain..."


class TestAssessNote:
    def test_runs_applicable_from_extracted_features(self) -> None:
        out = assess_note(_NOTE, DictExtractor(_HEART), presentation="chest pain")
        assert out["extracted_features"]["age_years"] == 58
        assert any(r["key"] == "heart" for r in out["applicable"])
        heart = next(r for r in out["applicable"] if r["key"] == "heart")
        assert heart["result"]["score"] == 3
        assert "not a medical device" in out["disclaimer"].lower()

    def test_partial_extraction_reports_gaps(self) -> None:
        # Only some HEART fields extracted -> HEART moves to needs_more_data.
        partial = {"history": "moderately_suspicious", "age_years": 58}
        out = assess_note(_NOTE, DictExtractor(partial), presentation="chest pain")
        assert not any(r["key"] == "heart" for r in out["applicable"])
        heart_gap = next(r for r in out["needs_more_data"] if r["key"] == "heart")
        assert "troponin" in heart_gap["missing_inputs"]

    def test_no_presentation_searches_whole_catalog(self) -> None:
        out = assess_note(_NOTE, DictExtractor(_HEART))
        assert any(r["key"] == "heart" for r in out["applicable"])


# --- A fake Anthropic client (no SDK, no network) ---------------------------


class _Block:
    def __init__(self, type: str, name: str | None = None, input: dict | None = None):
        self.type = type
        self.name = name
        self.input = input or {}


class _Message:
    def __init__(self, content: list[Any]):
        self.content = content


class _FakeMessages:
    def __init__(self, features: dict[str, Any]):
        self._features = features
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> _Message:
        self.calls.append(kwargs)
        return _Message([_Block("text"),
                         _Block("tool_use", "report_features", self._features)])


class _FakeClient:
    def __init__(self, features: dict[str, Any]):
        self.messages = _FakeMessages(features)


class TestClaudeExtractor:
    def test_extracts_tool_use_filtered_to_schema(self) -> None:
        # The model "returns" an extra field; it must be dropped to the schema.
        client = _FakeClient({**_HEART, "not_in_schema": 99})
        extractor = ClaudeExtractor(client=client, model="test-model")
        schema = union_schema(["heart"])
        out = extractor(_NOTE, schema)
        assert "not_in_schema" not in out
        assert out["history"] == "moderately_suspicious"

    def test_forces_the_tool_and_passes_optional_schema(self) -> None:
        client = _FakeClient(_HEART)
        extractor = ClaudeExtractor(client=client)
        extractor(_NOTE, union_schema(["heart"]))
        call = client.messages.calls[0]
        assert call["tool_choice"] == {"type": "tool", "name": "report_features"}
        assert call["tools"][0]["input_schema"]["required"] == []
        assert call["messages"][0]["content"] == _NOTE

    def test_returns_empty_when_no_tool_use(self) -> None:
        client = _FakeClient(_HEART)
        # Replace the response with text-only content.
        client.messages.create = lambda **k: _Message([_Block("text")])  # type: ignore[method-assign]
        extractor = ClaudeExtractor(client=client)
        assert extractor(_NOTE, union_schema(["heart"])) == {}

    def test_end_to_end_with_fake_client(self) -> None:
        client = _FakeClient(_HEART)
        out = assess_note(_NOTE, ClaudeExtractor(client=client),
                          presentation="chest pain")
        assert any(r["key"] == "heart" for r in out["applicable"])
