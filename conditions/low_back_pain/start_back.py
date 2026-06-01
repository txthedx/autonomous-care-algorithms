"""STarT Back Screening Tool for risk stratification in non-specific low back pain.

References:
    Hill JC, Dunn KM, Lewis M, et al.
        A primary care back pain screening tool: identifying patient subgroups
        for initial treatment. Arthritis Rheum. 2008;59(5):632-641.
        PMID: 18438893.
    Hill JC, Whitehurst DGT, Lewis M, et al.
        Comparison of stratified primary care management for low back pain
        with current best practice (STarT Back): a randomised controlled
        trial. Lancet. 2011;378(9802):1560-1571. PMID: 21963002.

This module scores the STarT Back tool and returns a risk stratification.
It applies to non-specific low back pain only; do not use it in patients with
unresolved red flags or identified specific pathology.

See DISCLAIMER.md at the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

BothersomeLevel = Literal["not_at_all", "slightly", "moderately", "very_much", "extremely"]

_BOTHERSOME_SCORING: frozenset[str] = frozenset({"moderately", "very_much", "extremely"})

RiskBand = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class StartBackResponses:
    """Patient responses to the nine STarT Back items.

    Items 1 through 8 are agree/disagree statements. `True` means the patient
    agrees. Item 9 is the bothersome-ness rating; values "moderately",
    "very_much", and "extremely" score 1 per Hill 2008.

    Attributes:
        leg_pain_in_last_2_weeks: "My back pain has spread down my leg(s) at
            some time in the last 2 weeks." (Item 1)
        shoulder_or_neck_pain_in_last_2_weeks: "I have had pain in the shoulder
            or neck at some time in the last 2 weeks." (Item 2)
        walked_only_short_distances: "I have only walked short distances because
            of my back pain." (Item 3)
        dressed_more_slowly: "In the last 2 weeks, I have dressed more slowly
            than usual because of back pain." (Item 4)
        not_safe_to_be_physically_active: "It is not really safe for a person
            with a condition like mine to be physically active." (Item 5)
        worrying_thoughts_a_lot: "Worrying thoughts have been going through my
            mind a lot of the time." (Item 6)
        pain_is_terrible_never_better: "I feel that my back pain is terrible
            and it is never going to get any better." (Item 7)
        not_enjoying_usual_things: "In general I have not enjoyed all the
            things I used to enjoy." (Item 8)
        bothersomeness: "Overall, how bothersome has your back pain been in
            the last 2 weeks?" (Item 9). One of "not_at_all", "slightly",
            "moderately", "very_much", "extremely".
    """

    leg_pain_in_last_2_weeks: bool
    shoulder_or_neck_pain_in_last_2_weeks: bool
    walked_only_short_distances: bool
    dressed_more_slowly: bool
    not_safe_to_be_physically_active: bool
    worrying_thoughts_a_lot: bool
    pain_is_terrible_never_better: bool
    not_enjoying_usual_things: bool
    bothersomeness: BothersomeLevel


@dataclass(frozen=True)
class StartBackResult:
    """STarT Back scoring and stratification result.

    Attributes:
        total_score: Sum of all nine items, range 0 to 9.
        psychosocial_subscale_score: Sum of items 5 through 9, range 0 to 5.
        risk_band: "low", "medium", or "high".
        recommended_management: Narrative recommendation aligned with the
            matched treatment arms in Hill 2011.
        rationale: Short justification.
        citations: Source short tags.
    """

    total_score: int
    psychosocial_subscale_score: int
    risk_band: RiskBand
    recommended_management: str
    rationale: str
    citations: tuple[str, ...]


def _bothersome_point(level: BothersomeLevel) -> int:
    if level not in {"not_at_all", "slightly", "moderately", "very_much", "extremely"}:
        raise ValueError(
            "bothersomeness must be one of: not_at_all, slightly, moderately, very_much, extremely"
        )
    return 1 if level in _BOTHERSOME_SCORING else 0


def start_back_score(responses: StartBackResponses) -> tuple[int, int]:
    """Compute the STarT Back total score and psychosocial subscale.

    Args:
        responses: The patient responses. See `StartBackResponses`.

    Returns:
        A tuple `(total_score, psychosocial_subscale_score)`.

    Raises:
        ValueError: If `bothersomeness` is not one of the allowed levels.
    """
    bothersome = _bothersome_point(responses.bothersomeness)

    psychosocial = (
        int(responses.not_safe_to_be_physically_active)
        + int(responses.worrying_thoughts_a_lot)
        + int(responses.pain_is_terrible_never_better)
        + int(responses.not_enjoying_usual_things)
        + bothersome
    )

    physical = (
        int(responses.leg_pain_in_last_2_weeks)
        + int(responses.shoulder_or_neck_pain_in_last_2_weeks)
        + int(responses.walked_only_short_distances)
        + int(responses.dressed_more_slowly)
    )

    return physical + psychosocial, psychosocial


def start_back_stratification(responses: StartBackResponses) -> StartBackResult:
    """Return the risk band and management recommendation per Hill 2008 and 2011.

    Args:
        responses: The patient responses. See `StartBackResponses`.

    Returns:
        A `StartBackResult` with total score, psychosocial subscale, risk band,
        and management recommendation.
    """
    total, psychosocial = start_back_score(responses)

    if total <= 3:
        return StartBackResult(
            total_score=total,
            psychosocial_subscale_score=psychosocial,
            risk_band="low",
            recommended_management=(
                "Education, reassurance, and self-management support. "
                "Most low-risk patients improve with minimal intervention."
            ),
            rationale="Total score of 3 or less corresponds to low risk of persistent disabling back pain.",
            citations=("Hill 2008", "Hill 2011"),
        )

    if psychosocial <= 3:
        return StartBackResult(
            total_score=total,
            psychosocial_subscale_score=psychosocial,
            risk_band="medium",
            recommended_management=(
                "Standardized physiotherapy targeting symptoms and function, "
                "as used in the matched-care arm of the Hill 2011 trial."
            ),
            rationale="Total score of 4 or more with psychosocial subscale of 3 or less corresponds to medium risk.",
            citations=("Hill 2008", "Hill 2011"),
        )

    return StartBackResult(
        total_score=total,
        psychosocial_subscale_score=psychosocial,
        risk_band="high",
        recommended_management=(
            "Combined physical and psychologically informed physiotherapy, "
            "as used in the matched-care arm of the Hill 2011 trial."
        ),
        rationale="Total score of 4 or more with psychosocial subscale of 4 or more corresponds to high risk.",
        citations=("Hill 2008", "Hill 2011"),
    )
