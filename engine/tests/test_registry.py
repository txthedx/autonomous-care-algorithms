"""Tests for the engine registry (the machine-readable catalog)."""

from __future__ import annotations

import importlib
import pathlib

import pytest

from engine import registry


class TestCatalog:
    def test_keys_present_and_unique(self) -> None:
        keys = registry.condition_keys()
        assert len(keys) >= 24
        assert len(keys) == len(set(keys))

    def test_list_conditions_shape(self) -> None:
        items = registry.list_conditions()
        assert items and all({"key", "label", "presentations"} <= set(i) for i in items)
        assert all(isinstance(i["presentations"], list) and i["presentations"] for i in items)

    def test_every_entry_resolves(self) -> None:
        # Each entry's module, function, and dataclasses must exist.
        for key in registry.condition_keys():
            entry = registry._entry(key)
            module = importlib.import_module(entry.module)
            assert callable(getattr(module, entry.fn))
            for cls_name in entry.dataclass_params:
                assert getattr(module, cls_name)

    def test_no_condition_module_left_unregistered(self) -> None:
        # Drift guard: every conditions/<pkg> with an __init__ must appear in
        # at least one registry entry.
        conditions_dir = pathlib.Path(__file__).resolve().parents[2] / "conditions"
        registered_modules = {registry._entry(k).module for k in registry.condition_keys()}
        for child in sorted(conditions_dir.iterdir()):
            if not child.is_dir() or child.name.startswith(("_", ".")):
                continue
            if not (child / "__init__.py").exists():
                continue
            module = f"conditions.{child.name}"
            assert module in registered_modules, f"{module} is not in the registry"


class TestSchema:
    def test_schema_for_every_condition(self) -> None:
        for key in registry.condition_keys():
            schema = registry.get_schema(key)
            assert schema["type"] == "object"
            assert schema["additionalProperties"] is False
            assert schema["properties"], key
            # Every property is required, and types are valid JSON Schema types.
            assert set(schema["required"]) == set(schema["properties"])
            for prop in schema["properties"].values():
                assert prop["type"] in {"boolean", "integer", "number", "string"}
                if prop["type"] == "string" and "enum" in prop:
                    assert prop["enum"]

    def test_enum_options_match_literal(self) -> None:
        # HEART's history field is a Literal -> string enum.
        schema = registry.get_schema("heart")
        history = schema["properties"]["history"]
        assert history == {"type": "string",
                           "enum": ["slightly_suspicious", "moderately_suspicious",
                                    "highly_suspicious"]}

    def test_scalar_param_in_schema(self) -> None:
        # PERC has a scalar boolean parameter appended after the dataclass.
        schema = registry.get_schema("perc")
        assert schema["properties"]["pretest_probability_is_low"] == {"type": "boolean"}

    def test_multi_dataclass_schema_is_flattened(self) -> None:
        # Ottawa ankle = AnkleAssessmentFeatures + ApplicabilityFactors.
        schema = registry.get_schema("ottawa_ankle")
        assert "pain_in_malleolar_zone" in schema["properties"]   # from features
        assert "intoxication" in schema["properties"]             # from applicability


class TestRunEquivalence:
    """`run` must equal calling the underlying function directly."""

    def test_heart_single_dataclass(self) -> None:
        from conditions.chest_pain import HeartFeatures, heart_assessment
        feats = dict(
            history="moderately_suspicious", ecg="normal", age_years=58,
            hypertension=True, hypercholesterolemia=True, diabetes_mellitus=False,
            current_or_recent_smoking=False, family_history_of_cad=False,
            obesity_bmi_over_30=False, history_of_atherosclerotic_disease=False,
            troponin="at_or_below_normal_limit",
        )
        direct = heart_assessment(HeartFeatures(**feats))
        assert registry.run("heart", feats)["score"] == direct.score
        assert registry.run("heart", feats)["risk_band"] == direct.risk_band

    def test_perc_dataclass_plus_scalar(self) -> None:
        feats = {
            "age_50_or_older": False, "heart_rate_100_or_more": False,
            "spo2_below_95_on_room_air": False, "hemoptysis": False,
            "estrogen_use": False, "prior_dvt_or_pe": False,
            "unilateral_leg_swelling": False,
            "recent_surgery_or_trauma_within_4_weeks_requiring_hospitalization": False,
            "pretest_probability_is_low": True,
        }
        result = registry.run("perc", feats)
        assert result["pe_ruled_out"] is True

    def test_ottawa_ankle_two_dataclasses(self) -> None:
        feats = {
            "pain_in_malleolar_zone": True,
            "tender_lateral_malleolus_distal_6cm": False,
            "tender_medial_malleolus_distal_6cm": False,
            "unable_to_bear_weight_immediately_and_now": True,
            "age_under_18": False, "intoxication": False,
            "distracting_injury": False,
            "decreased_sensation_or_neurologic_deficit": False,
            "gross_deformity": False, "isolated_skin_injury": False,
            "head_injury_or_decreased_consciousness": False,
        }
        result = registry.run("ottawa_ankle", feats)
        assert result["imaging_indicated"] is True

    def test_kdigo_floats(self) -> None:
        feats = {"egfr_ml_min_1_73m2": 35.0, "acr_mg_per_mmol": 12.0,
                 "persistent_over_3_months": True}
        result = registry.run("kdigo", feats)
        assert result["stage_label"] == "G3bA2"

    def test_result_is_jsonable(self) -> None:
        import json
        feats = {"egfr_ml_min_1_73m2": 100.0, "acr_mg_per_mmol": 1.0,
                 "persistent_over_3_months": True}
        json.dumps(registry.run("kdigo", feats))  # must not raise


class TestValidation:
    def test_missing_required(self) -> None:
        errors = registry.validate("kdigo", {"egfr_ml_min_1_73m2": 50.0})
        assert any("missing required input" in e for e in errors)

    def test_unknown_input(self) -> None:
        errors = registry.validate("kdigo", {
            "egfr_ml_min_1_73m2": 50.0, "acr_mg_per_mmol": 1.0,
            "persistent_over_3_months": True, "bogus": 1,
        })
        assert any("unknown input: bogus" in e for e in errors)

    def test_bad_enum(self) -> None:
        errors = registry.validate("four_at", {
            "alertness": "WRONG", "amt4": "no_mistakes",
            "attention_months_backwards": "seven_or_more_correct",
            "acute_change_or_fluctuating_course": False,
        })
        assert any("alertness must be one of" in e for e in errors)

    def test_valid_features_no_errors(self) -> None:
        feats = {"egfr_ml_min_1_73m2": 50.0, "acr_mg_per_mmol": 1.0,
                 "persistent_over_3_months": True}
        assert registry.validate("kdigo", feats) == []

    def test_missing_inputs_helper(self) -> None:
        assert set(registry.missing_inputs("kdigo", {"egfr_ml_min_1_73m2": 50.0})) == {
            "acr_mg_per_mmol", "persistent_over_3_months"}

    def test_run_raises_on_invalid(self) -> None:
        with pytest.raises(ValueError):
            registry.run("kdigo", {"egfr_ml_min_1_73m2": 50.0})

    def test_run_raises_on_unknown_condition(self) -> None:
        with pytest.raises(KeyError):
            registry.run("not_a_condition", {})

    def test_run_surfaces_algorithm_value_error(self) -> None:
        # Negative eGFR is rejected by the underlying algorithm.
        with pytest.raises(ValueError):
            registry.run("kdigo", {"egfr_ml_min_1_73m2": -1.0,
                                   "acr_mg_per_mmol": 1.0,
                                   "persistent_over_3_months": True})


class TestDescribe:
    def test_describe_includes_schema_and_disclaimer(self) -> None:
        d = registry.describe("heart")
        assert d["key"] == "heart"
        assert d["input_schema"]["type"] == "object"
        assert "not a medical device" in d["disclaimer"].lower()
