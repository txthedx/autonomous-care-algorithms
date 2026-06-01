"""Tests for the Bent 2002 UTI decision rule.

Coverage targets:
- Each complicating factor independently triggers the complicated path.
- Complicating factors take precedence over symptom count and vaginal symptoms.
- Vaginal symptoms (discharge or irritation) trigger the alternative
  diagnoses path when no complicating factors are present.
- Symptom-count boundaries: 0 -> low, 1 -> intermediate, 2+ -> high.
- Each cardinal symptom counts independently.
- Output shape: probability band, recommended action, citations, rationale.
"""

from __future__ import annotations

import pytest

from conditions.urinary_tract_infection.assessment import (
    UtiComplicatingFactors,
    UtiPresentingFeatures,
    uti_assessment,
)

_SYMPTOMS_DEFAULT: dict[str, bool] = {
    "dysuria": False,
    "urinary_frequency": False,
    "hematuria": False,
    "suprapubic_or_back_pain": False,
    "vaginal_discharge": False,
    "vaginal_irritation": False,
}

_FACTORS_DEFAULT: dict[str, bool] = {
    "pregnancy": False,
    "male": False,
    "diabetes_uncontrolled_or_immunocompromise": False,
    "indwelling_catheter_or_recent_instrumentation": False,
    "known_urinary_tract_abnormality": False,
    "recent_antibiotic_use": False,
    "symptoms_more_than_7_days": False,
    "recurrent_uti": False,
    "flank_pain_or_fever_or_systemic_symptoms": False,
}

_COMPLICATING_FIELDS: tuple[str, ...] = tuple(_FACTORS_DEFAULT.keys())


def _symptoms(**overrides: bool) -> UtiPresentingFeatures:
    return UtiPresentingFeatures(**(_SYMPTOMS_DEFAULT | overrides))


def _factors(**overrides: bool) -> UtiComplicatingFactors:
    return UtiComplicatingFactors(**(_FACTORS_DEFAULT | overrides))


class TestComplicatingFactors:
    @pytest.mark.parametrize("field", _COMPLICATING_FIELDS)
    def test_each_complicating_factor_triggers_complicated_path(self, field: str) -> None:
        result = uti_assessment(
            _symptoms(dysuria=True, urinary_frequency=True),
            _factors(**{field: True}),
        )
        assert result.is_complicated_pattern is True
        assert result.pretest_probability_band == "not_applicable_complicated"
        assert len(result.complicating_factors_present) == 1

    def test_multiple_factors_listed(self) -> None:
        result = uti_assessment(
            _symptoms(dysuria=True),
            _factors(pregnancy=True, recurrent_uti=True),
        )
        assert result.is_complicated_pattern is True
        assert len(result.complicating_factors_present) == 2

    def test_complicating_overrides_symptom_count(self) -> None:
        result = uti_assessment(
            _symptoms(
                dysuria=True,
                urinary_frequency=True,
                hematuria=True,
                suprapubic_or_back_pain=True,
            ),
            _factors(pregnancy=True),
        )
        assert result.pretest_probability_band == "not_applicable_complicated"

    def test_complicated_recommendation_mentions_culture_and_broader_workup(self) -> None:
        result = uti_assessment(
            _symptoms(dysuria=True),
            _factors(flank_pain_or_fever_or_systemic_symptoms=True),
        )
        assert "culture" in result.recommended_action.lower()
        assert "broader workup" in result.recommended_action.lower()


class TestVaginalSymptoms:
    def test_vaginal_discharge_alone_triggers_alternative_diagnoses(self) -> None:
        result = uti_assessment(_symptoms(vaginal_discharge=True), _factors())
        assert result.is_complicated_pattern is False
        assert result.vaginal_symptoms_present is True
        assert result.pretest_probability_band == "alternative_diagnoses_considered"

    def test_vaginal_irritation_alone_triggers_alternative_diagnoses(self) -> None:
        result = uti_assessment(_symptoms(vaginal_irritation=True), _factors())
        assert result.pretest_probability_band == "alternative_diagnoses_considered"

    def test_vaginal_symptoms_override_uti_symptoms(self) -> None:
        result = uti_assessment(
            _symptoms(
                dysuria=True,
                urinary_frequency=True,
                vaginal_discharge=True,
            ),
            _factors(),
        )
        assert result.pretest_probability_band == "alternative_diagnoses_considered"

    def test_complicating_factors_take_precedence_over_vaginal_symptoms(self) -> None:
        result = uti_assessment(
            _symptoms(vaginal_discharge=True),
            _factors(pregnancy=True),
        )
        assert result.pretest_probability_band == "not_applicable_complicated"

    def test_vaginal_recommendation_mentions_pelvic_exam(self) -> None:
        result = uti_assessment(_symptoms(vaginal_discharge=True), _factors())
        assert "pelvic" in result.recommended_action.lower()


class TestSymptomCount:
    def test_zero_symptoms_is_low(self) -> None:
        result = uti_assessment(_symptoms(), _factors())
        assert result.uti_symptom_count == 0
        assert result.pretest_probability_band == "low"

    @pytest.mark.parametrize(
        "field",
        ["dysuria", "urinary_frequency", "hematuria", "suprapubic_or_back_pain"],
    )
    def test_each_single_symptom_yields_intermediate(self, field: str) -> None:
        result = uti_assessment(_symptoms(**{field: True}), _factors())
        assert result.uti_symptom_count == 1
        assert result.pretest_probability_band == "intermediate"

    def test_two_symptoms_yields_high(self) -> None:
        result = uti_assessment(
            _symptoms(dysuria=True, urinary_frequency=True),
            _factors(),
        )
        assert result.uti_symptom_count == 2
        assert result.pretest_probability_band == "high"

    def test_three_symptoms_yields_high(self) -> None:
        result = uti_assessment(
            _symptoms(dysuria=True, urinary_frequency=True, hematuria=True),
            _factors(),
        )
        assert result.uti_symptom_count == 3
        assert result.pretest_probability_band == "high"

    def test_all_four_symptoms_yields_high(self) -> None:
        result = uti_assessment(
            _symptoms(
                dysuria=True,
                urinary_frequency=True,
                hematuria=True,
                suprapubic_or_back_pain=True,
            ),
            _factors(),
        )
        assert result.uti_symptom_count == 4
        assert result.pretest_probability_band == "high"


class TestRecommendations:
    def test_low_recommends_alternative_causes(self) -> None:
        result = uti_assessment(_symptoms(), _factors())
        assert "alternative" in result.recommended_action.lower()

    def test_intermediate_recommends_urinalysis_or_culture(self) -> None:
        result = uti_assessment(_symptoms(dysuria=True), _factors())
        action = result.recommended_action.lower()
        assert "urinalysis" in action or "dipstick" in action or "culture" in action

    def test_high_recommends_empirical_treatment(self) -> None:
        result = uti_assessment(
            _symptoms(dysuria=True, urinary_frequency=True),
            _factors(),
        )
        assert "empirical" in result.recommended_action.lower()

    def test_high_acknowledges_local_resistance(self) -> None:
        result = uti_assessment(
            _symptoms(dysuria=True, urinary_frequency=True),
            _factors(),
        )
        assert "resistance" in result.recommended_action.lower()


class TestOutputShape:
    def test_citations_present_in_every_branch(self) -> None:
        for symptoms, factors in [
            (_symptoms(), _factors()),
            (_symptoms(dysuria=True), _factors()),
            (_symptoms(dysuria=True, urinary_frequency=True), _factors()),
            (_symptoms(vaginal_discharge=True), _factors()),
            (_symptoms(dysuria=True), _factors(pregnancy=True)),
        ]:
            result = uti_assessment(symptoms, factors)
            assert "Bent 2002" in result.citations
            assert result.rationale.strip() != ""


class TestClinicalVignettes:
    """Abstract vignettes that exercise the rule at decision boundaries.

    No real patient data; vignettes test the rule's logical structure only.
    """

    def test_classic_uncomplicated_cystitis_pattern_yields_high(self) -> None:
        result = uti_assessment(
            _symptoms(dysuria=True, urinary_frequency=True),
            _factors(),
        )
        assert result.pretest_probability_band == "high"
        assert "empirical" in result.recommended_action.lower()

    def test_pregnant_patient_with_classic_symptoms_is_complicated(self) -> None:
        result = uti_assessment(
            _symptoms(dysuria=True, urinary_frequency=True),
            _factors(pregnancy=True),
        )
        assert result.is_complicated_pattern is True

    def test_suspected_pyelonephritis_is_complicated(self) -> None:
        result = uti_assessment(
            _symptoms(dysuria=True, urinary_frequency=True, suprapubic_or_back_pain=True),
            _factors(flank_pain_or_fever_or_systemic_symptoms=True),
        )
        assert result.is_complicated_pattern is True

    def test_isolated_dysuria_with_vaginal_discharge_points_to_other_causes(self) -> None:
        result = uti_assessment(
            _symptoms(dysuria=True, vaginal_discharge=True),
            _factors(),
        )
        assert result.pretest_probability_band == "alternative_diagnoses_considered"
