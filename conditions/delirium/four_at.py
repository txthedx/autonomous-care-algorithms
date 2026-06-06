"""4AT rapid delirium screening instrument.

References:
    Bellelli G, Morandi A, Davis DH, et al.
        Validation of the 4AT, a new instrument for rapid delirium screening:
        a study in 234 hospitalised older people. Age Ageing. 2014;43(4):
        496-502. PMID: 24590568.
    Shenkin SD, Fox C, Godfrey M, et al.
        Delirium detection in older acute medical inpatients: a multicentre
        prospective comparative diagnostic test accuracy study of the 4AT and
        the confusion assessment method. BMC Med. 2019;17(1):138.
        PMID: 31337404.

The 4AT is a four-item bedside instrument for rapid delirium screening in older
adults. It takes about two minutes, requires no special training, and can be
applied to patients who cannot complete cognitive testing because of drowsiness
or agitation. It is endorsed by SIGN, NICE, and the European Delirium
Association. The four items are Alertness, AMT4 (an abbreviated orientation
test), Attention (months of the year backwards), and Acute change or
fluctuating course, for a total of 0 to 12.

The 4AT is a screening tool, not a diagnostic test: a score of 4 or above
indicates possible delirium and warrants a full clinical assessment, not an
automatic diagnosis. See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

AlertnessLevel = Literal["normal", "altered"]
Amt4Level = Literal[
    "no_mistakes",
    "one_mistake",
    "two_or_more_mistakes_or_untestable",
]
AttentionLevel = Literal[
    "seven_or_more_correct",
    "fewer_than_seven_or_refuses",
    "untestable",
]
InterpretationBand = Literal[
    "unlikely",
    "possible_cognitive_impairment",
    "possible_delirium",
]


@dataclass(frozen=True)
class FourATFeatures:
    """Responses for the four 4AT items.

    Attributes:
        alertness: Observed alertness. "normal" (fully alert, or mild
            sleepiness for < 10 seconds after waking then normal) scores 0;
            "altered" (clearly abnormal — markedly drowsy, stuporous, or
            agitated/hyperactive) scores 4.
        amt4: Abbreviated Mental Test 4 — age, date of birth, place (name of
            the hospital or building), and current year. "no_mistakes" (0),
            "one_mistake" (1), "two_or_more_mistakes_or_untestable" (2).
        attention_months_backwards: Months of the year in reverse from
            December. "seven_or_more_correct" (0),
            "fewer_than_seven_or_refuses" (1, starts but fewer than seven
            months correct, or refuses to start), "untestable" (2, cannot
            start because unwell, drowsy, or inattentive).
        acute_change_or_fluctuating_course: Significant change or fluctuation
            in alertness, cognition, or other mental function arising over the
            last two weeks and still evident in the last 24 hours. Scores 4 if
            present, 0 if absent.
    """

    alertness: AlertnessLevel
    amt4: Amt4Level
    attention_months_backwards: AttentionLevel
    acute_change_or_fluctuating_course: bool


@dataclass(frozen=True)
class FourATComponentScores:
    """Per-item point breakdown for the 4AT.

    Attributes:
        alertness: Alertness item points (0 or 4).
        amt4: AMT4 item points (0-2).
        attention: Attention item points (0-2).
        acute_change: Acute change / fluctuation item points (0 or 4).
    """

    alertness: int
    amt4: int
    attention: int
    acute_change: int


@dataclass(frozen=True)
class FourATResult:
    """4AT assessment result.

    Attributes:
        score: Total 4AT score, range 0 to 12.
        components: Per-item point breakdown.
        interpretation_band: "unlikely" (0), "possible_cognitive_impairment"
            (1-3), or "possible_delirium" (>= 4).
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Conditions under which the screen must be
            interpreted with care.
        citations: Source short tags.
    """

    score: int
    components: FourATComponentScores
    interpretation_band: InterpretationBand
    recommended_action: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


_ALERTNESS_POINTS: dict[str, int] = {"normal": 0, "altered": 4}
_AMT4_POINTS: dict[str, int] = {
    "no_mistakes": 0,
    "one_mistake": 1,
    "two_or_more_mistakes_or_untestable": 2,
}
_ATTENTION_POINTS: dict[str, int] = {
    "seven_or_more_correct": 0,
    "fewer_than_seven_or_refuses": 1,
    "untestable": 2,
}

_POPULATION_CAVEATS: tuple[str, ...] = (
    "The 4AT is a screening tool, not a diagnostic test. A score of 4 or above "
    "indicates possible delirium and warrants a full clinical assessment, not "
    "an automatic diagnosis.",
    "A single 4AT does not distinguish delirium from dementia; serial "
    "assessment, the trajectory of change, and collateral history matter. "
    "Item 4 (acute change or fluctuation) is central to that distinction.",
    "Item 4 requires reliable information about the patient's baseline and "
    "recent course. If that information is unavailable, a low total score does "
    "not exclude delirium.",
    "Validated in hospitalised older adults; performance in other settings or "
    "younger populations may differ.",
)


def four_at_component_scores(features: FourATFeatures) -> FourATComponentScores:
    """Return the per-item point breakdown for the 4AT.

    Args:
        features: The four 4AT item responses. See `FourATFeatures`.

    Returns:
        A `FourATComponentScores`.
    """
    return FourATComponentScores(
        alertness=_ALERTNESS_POINTS[features.alertness],
        amt4=_AMT4_POINTS[features.amt4],
        attention=_ATTENTION_POINTS[features.attention_months_backwards],
        acute_change=4 if features.acute_change_or_fluctuating_course else 0,
    )


def four_at_score(features: FourATFeatures) -> int:
    """Compute the total 4AT score, range 0 to 12.

    Args:
        features: The four 4AT item responses. See `FourATFeatures`.

    Returns:
        The integer 4AT score.
    """
    components = four_at_component_scores(features)
    return (
        components.alertness
        + components.amt4
        + components.attention
        + components.acute_change
    )


def four_at_assessment(features: FourATFeatures) -> FourATResult:
    """Compute the 4AT score and its interpretation band.

    Args:
        features: The four 4AT item responses. See `FourATFeatures`.

    Returns:
        A `FourATResult`.
    """
    components = four_at_component_scores(features)
    score = (
        components.alertness
        + components.amt4
        + components.attention
        + components.acute_change
    )
    citations = ("Bellelli 2014",)

    if score == 0:
        return FourATResult(
            score=score,
            components=components,
            interpretation_band="unlikely",
            recommended_action=(
                "Delirium and moderate-to-severe cognitive impairment are "
                "unlikely on this screen. Re-screen if clinical suspicion "
                "changes; delirium can be missed if the acute-change "
                "information is incomplete."
            ),
            rationale="A 4AT score of 0 indicates delirium and moderate-to-severe cognitive impairment are unlikely.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    if score <= 3:
        return FourATResult(
            score=score,
            components=components,
            interpretation_band="possible_cognitive_impairment",
            recommended_action=(
                "Possible cognitive impairment. A score of 1 to 3 more often "
                "reflects chronic cognitive impairment than delirium; arrange "
                "further cognitive assessment and review collateral history, "
                "and reassess if the picture changes."
            ),
            rationale="A 4AT score of 1 to 3 suggests possible cognitive impairment rather than delirium.",
            population_caveats=_POPULATION_CAVEATS,
            citations=citations,
        )

    return FourATResult(
        score=score,
        components=components,
        interpretation_band="possible_delirium",
        recommended_action=(
            "Possible delirium, with or without cognitive impairment. "
            "Undertake a full clinical assessment for delirium, identify and "
            "treat precipitants, and review medications. The 4AT is a screen, "
            "not a diagnosis."
        ),
        rationale="A 4AT score of 4 or above suggests possible delirium.",
        population_caveats=_POPULATION_CAVEATS,
        citations=citations,
    )
