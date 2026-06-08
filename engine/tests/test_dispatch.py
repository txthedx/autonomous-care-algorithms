"""Tests for engine dispatch (applicability over the catalog)."""

from __future__ import annotations

from engine import dispatch

# A bag of features that fully satisfies KDIGO and the San Francisco Syncope
# Rule (no field-name overlap between the two).
_KDIGO = {
    "egfr_ml_min_1_73m2": 35.0,
    "acr_mg_per_mmol": 12.0,
    "persistent_over_3_months": True,
}
_SFSR = {
    "congestive_heart_failure_history": False,
    "hematocrit_percent": 42.0,
    "abnormal_ecg": True,
    "shortness_of_breath": False,
    "systolic_bp_mmhg": 128,
}


class TestPresentations:
    def test_presentations_listed(self) -> None:
        tags = dispatch.presentations()
        assert "chest pain" in tags
        assert tags == sorted(tags)

    def test_by_presentation_pulmonary_embolism(self) -> None:
        keys = dispatch.by_presentation("pulmonary embolism")
        assert "wells_pe_2t" in keys
        assert "perc" in keys

    def test_by_presentation_substring_match(self) -> None:
        # "chest" should match the "chest pain" tag.
        assert "heart" in dispatch.by_presentation("chest")


class TestSuggest:
    def test_runnable_first(self) -> None:
        records = dispatch.suggest(_KDIGO)
        kdigo = next(r for r in records if r["key"] == "kdigo")
        assert kdigo["runnable"] is True
        assert kdigo["missing_inputs"] == []
        # Runnable records sort ahead of any with missing inputs.
        assert records[0]["runnable"] is True

    def test_missing_inputs_reported(self) -> None:
        records = dispatch.suggest({"egfr_ml_min_1_73m2": 50.0})
        kdigo = next(r for r in records if r["key"] == "kdigo")
        assert kdigo["runnable"] is False
        assert set(kdigo["missing_inputs"]) == {"acr_mg_per_mmol",
                                                "persistent_over_3_months"}

    def test_presentation_filter_narrows(self) -> None:
        records = dispatch.suggest({}, presentation="syncope")
        keys = {r["key"] for r in records}
        assert "sfsr" in keys
        assert "kdigo" not in keys


class TestRunApplicable:
    def test_runs_every_satisfied_algorithm(self) -> None:
        out = dispatch.run_applicable({**_KDIGO, **_SFSR})
        applicable_keys = {r["key"] for r in out["applicable"]}
        assert "kdigo" in applicable_keys
        assert "sfsr" in applicable_keys

    def test_results_carry_citations(self) -> None:
        out = dispatch.run_applicable(_KDIGO)
        kdigo = next(r for r in out["applicable"] if r["key"] == "kdigo")
        assert kdigo["result"]["stage_label"] == "G3bA2"
        assert kdigo["result"]["citations"]

    def test_extra_fields_are_ignored_per_algorithm(self) -> None:
        # KDIGO runs even though the bag also carries SFSR fields it never reads.
        out = dispatch.run_applicable({**_KDIGO, **_SFSR})
        kdigo = next(r for r in out["applicable"] if r["key"] == "kdigo")
        assert kdigo["result"]["gfr_category"] == "G3b"

    def test_needs_more_data_listed(self) -> None:
        out = dispatch.run_applicable({"egfr_ml_min_1_73m2": 50.0})
        needs = {r["key"] for r in out["needs_more_data"]}
        assert "kdigo" in needs
        kdigo = next(r for r in out["needs_more_data"] if r["key"] == "kdigo")
        assert "acr_mg_per_mmol" in kdigo["missing_inputs"]

    def test_include_unmet_false_omits_needs(self) -> None:
        out = dispatch.run_applicable(_KDIGO, include_unmet=False)
        assert out["needs_more_data"] == []

    def test_out_of_range_value_goes_to_errors(self) -> None:
        bad = {"egfr_ml_min_1_73m2": -1.0, "acr_mg_per_mmol": 1.0,
               "persistent_over_3_months": True}
        out = dispatch.run_applicable(bad)
        error_keys = {r["key"] for r in out["errors"]}
        assert "kdigo" in error_keys
        assert "kdigo" not in {r["key"] for r in out["applicable"]}

    def test_presentation_filter_on_run(self) -> None:
        out = dispatch.run_applicable(_SFSR, presentation="syncope")
        assert {r["key"] for r in out["applicable"]} == {"sfsr"}

    def test_disclaimer_present(self) -> None:
        out = dispatch.run_applicable(_KDIGO)
        assert "not a medical device" in out["disclaimer"].lower()

    def test_empty_features_runs_nothing(self) -> None:
        out = dispatch.run_applicable({})
        assert out["applicable"] == []
        assert out["needs_more_data"]  # everything needs data
