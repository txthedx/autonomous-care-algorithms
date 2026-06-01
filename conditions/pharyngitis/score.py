"""McIsaac (modified Centor) score for acute pharyngitis.

References:
    Centor RM, Witherspoon JM, Dalton HP, Brody CE, Link K.
        The diagnosis of strep throat in adults in the emergency room.
        Med Decis Making. 1981;1(3):239-46. PMID: 6763125.
    McIsaac WJ, White D, Tannis D, Low DE.
        A clinical score to reduce unnecessary antibiotic use in patients
        with sore throat. CMAJ. 1998;158(1):75-83. PMID: 9475915.
    McIsaac WJ, Kellner JD, Aufricht P, Vanjaka A, Low DE.
        Empirical validation of guidelines for the management of pharyngitis
        in children and adults. JAMA. 2004;291(13):1587-95. PMID: 15069046.
    Shulman ST, Bisno AL, Clegg HW, et al. (IDSA).
        Clinical practice guideline for the diagnosis and management of
        group A streptococcal pharyngitis: 2012 update.
        Clin Infect Dis. 2012;55(10):e86-102. PMID: 22965026.

This module computes a score and returns a recommendation band. It does not
diagnose, prescribe, or replace clinical judgment. See DISCLAIMER.md at the
repository root.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PharyngitisFeatures:
    """Clinical features for the McIsaac score.

    Attributes:
        age_years: Patient age in completed years. Must be non-negative.
        history_of_fever: History of fever >38°C (100.4°F) or measured fever.
        tonsillar_exudate: Tonsillar swelling or exudate on examination.
        tender_anterior_cervical_nodes: Tender anterior cervical lymphadenopathy.
        no_cough: True if cough is absent. The Centor criterion awards a point
            for the *absence* of cough.
    """

    age_years: int
    history_of_fever: bool
    tonsillar_exudate: bool
    tender_anterior_cervical_nodes: bool
    no_cough: bool


@dataclass(frozen=True)
class Recommendation:
    """Score-based recommendation aligned to IDSA 2012.

    Attributes:
        score: The McIsaac score, range -1 to 5.
        gas_probability_band: Approximate GAS probability band from McIsaac 2004.
            Population-level estimate; depends on local prevalence.
        action: Recommended action consistent with IDSA 2012.
        rationale: One-sentence justification.
        citations: Short citation tags. See references.bib for full entries.
    """

    score: int
    gas_probability_band: str
    action: str
    rationale: str
    citations: tuple[str, ...]


def mcisaac_score(features: PharyngitisFeatures) -> int:
    """Compute the McIsaac (modified Centor) score.

    The score is the sum of the four Centor criteria plus an age adjustment:
    +1 for ages 3 to 14, 0 for ages 15 to 44, and -1 for ages 45 or older.
    Total range is -1 to 5.

    Args:
        features: The clinical features. See `PharyngitisFeatures`.

    Returns:
        Integer score in the range -1 to 5.

    Raises:
        ValueError: If `age_years` is negative.
    """
    if features.age_years < 0:
        raise ValueError("age_years must be non-negative")

    centor_points = (
        int(features.history_of_fever)
        + int(features.tonsillar_exudate)
        + int(features.tender_anterior_cervical_nodes)
        + int(features.no_cough)
    )

    if 3 <= features.age_years <= 14:
        age_adjustment = 1
    elif features.age_years >= 45:
        age_adjustment = -1
    else:
        age_adjustment = 0

    return centor_points + age_adjustment


def mcisaac_recommendation(features: PharyngitisFeatures) -> Recommendation:
    """Return the recommendation band for the given clinical features.

    Recommendations follow IDSA 2012, which favors test-confirmed treatment
    over empirical antibiotics in adults. Children with a negative RADT
    should have backup culture.

    Args:
        features: The clinical features. See `PharyngitisFeatures`.

    Returns:
        A `Recommendation` with score, probability band, action, rationale,
        and citations.
    """
    score = mcisaac_score(features)

    if score <= 0:
        return Recommendation(
            score=score,
            gas_probability_band="very low (~1 to 2.5%)",
            action="No testing. No antibiotics. Symptomatic care.",
            rationale="GAS is unlikely; testing risks false positives and overtreatment.",
            citations=("McIsaac 1998", "McIsaac 2004", "Shulman 2012"),
        )

    if score == 1:
        return Recommendation(
            score=score,
            gas_probability_band="low (~5 to 10%)",
            action="No routine testing in adults. No empirical antibiotics.",
            rationale="Pretest probability is below the threshold for routine RADT in adults.",
            citations=("McIsaac 1998", "McIsaac 2004", "Shulman 2012"),
        )

    if score in (2, 3):
        return Recommendation(
            score=score,
            gas_probability_band="intermediate (~11 to 35%)",
            action=(
                "Perform RADT. Treat only if positive. "
                "In children with a negative RADT, send backup throat culture."
            ),
            rationale="Clinical features alone are insufficient; test-confirmed treatment minimizes unnecessary antibiotics.",
            citations=("Shulman 2012",),
        )

    return Recommendation(
        score=score,
        gas_probability_band="high (~50% or more)",
        action=(
            "Perform RADT. Treat only if positive. "
            "IDSA 2012 does not endorse empirical antibiotics in adults without test confirmation."
        ),
        rationale="Even at high scores, empirical treatment exposes false-positive patients to needless antibiotics.",
        citations=("McIsaac 2004", "Shulman 2012"),
    )
