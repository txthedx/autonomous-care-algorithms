"""Finasteride safety screens: teratogenicity and pre-prescribe psychiatric screen.

References:
    U.S. Food and Drug Administration. PROPECIA (finasteride) tablets —
        prescribing information. NDA 020788. (Pregnancy contraindication;
        teratogenicity.)
    Health Canada. Summary Safety Review — finasteride; and the January 2024
        update to the Canadian product monographs for Propecia and Proscar
        (Warnings and Precautions: mood alterations, suicidal ideation,
        self-harm). (Pre-prescribe psychiatric screen.)

Finasteride is a Type II 5α-reductase inhibitor used for male androgenetic
alopecia and benign prostatic hyperplasia. Two distinct, deterministic safety
checks matter at prescribing:

1. ``finasteride_contraindication`` — finasteride is **contraindicated in
   pregnancy and in anyone who is or may become pregnant**: by lowering
   dihydrotestosterone it can cause abnormalities of the external genitalia of a
   male fetus (teratogenic; historically FDA Pregnancy Category X). Pregnant
   people should also avoid handling crushed or broken tablets.

2. ``finasteride_psychiatric_screen`` — Health Canada (January 2024) updated the
   Canadian product monographs with mood alterations — depressed mood,
   depression, self-harm, and suicidal ideation, including worsening of
   pre-existing depression — and recommends screening every patient for
   suicidal ideation, self-harm, and depression **before** prescribing. Active
   suicidal ideation or self-harm blocks initiation; a depression history routes
   to clinician review.

Inputs are structured features (booleans). Outputs are contraindication and
screen verdicts — never prescriptions, doses, or routes. The screens cover only
these two issues; they are not a full eligibility or psychiatric assessment and
support, rather than replace, clinical judgement. See DISCLAIMER.md at the
repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ContraindicationVerdict = Literal[
    "absolute_contraindication",
    "no_contraindication_detected",
]

PsychiatricVerdict = Literal[
    "active_risk_do_not_initiate",
    "history_clinician_review",
    "screen_negative",
]

_CONTRAINDICATION_CAVEATS: tuple[str, ...] = (
    "Captures the reproductive situation (is, or may become, pregnant), not "
    "gender identity: finasteride is teratogenic to a male fetus, so the "
    "contraindication applies to anyone able to become pregnant.",
    "Pregnant people should not handle crushed or broken finasteride tablets "
    "(potential absorption); intact tablets are coated (PROPECIA label).",
    "Screens only the teratogenicity contraindication; it is not a full "
    "eligibility, interaction, or jurisdiction review.",
    "Supports but does not replace clinical judgement; the output is a "
    "contraindication verdict, not a prescription. See DISCLAIMER.md.",
)

_PSYCHIATRIC_CAVEATS: tuple[str, ...] = (
    "Health Canada (January 2024) added mood alterations — depressed mood, "
    "depression, self-harm, and suicidal ideation, including worsening of "
    "pre-existing depression — to the Canadian product monographs and "
    "recommends screening every patient before prescribing.",
    "A negative screen is not reassurance to skip counselling: advise on the "
    "mood-alteration risk and document the screen regardless of the result.",
    "Post-marketing psychiatric symptoms have been reported to continue after "
    "finasteride is stopped; this screen addresses initiation only.",
    "Not a validated suicide-risk instrument and not a substitute for clinical "
    "assessment; a positive screen routes to the appropriate clinical pathway. "
    "See DISCLAIMER.md.",
)


@dataclass(frozen=True)
class FinasterideContraindicationFeatures:
    """Inputs for the finasteride teratogenicity contraindication screen.

    Attributes:
        pregnant_or_able_to_become_pregnant: The patient is pregnant or is a
            person of reproductive potential who could become pregnant.
    """

    pregnant_or_able_to_become_pregnant: bool


@dataclass(frozen=True)
class FinasterideContraindicationResult:
    """Result of the teratogenicity contraindication screen.

    Attributes:
        verdict: ``absolute_contraindication`` if pregnancy or reproductive
            potential is present, else ``no_contraindication_detected``.
        contraindicated: True when the verdict is an absolute contraindication.
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Scope and interpretation caveats.
        citations: Source short tags.
    """

    verdict: ContraindicationVerdict
    contraindicated: bool
    recommended_action: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


@dataclass(frozen=True)
class FinasteridePsychiatricFeatures:
    """Inputs for the pre-prescribe psychiatric screen.

    Attributes:
        active_suicidal_ideation_or_self_harm: Current suicidal ideation or
            self-harm on screening.
        current_or_past_depression: Current or past depression (including
            previously treated depression), without active suicidal ideation.
    """

    active_suicidal_ideation_or_self_harm: bool
    current_or_past_depression: bool


@dataclass(frozen=True)
class FinasteridePsychiatricResult:
    """Result of the pre-prescribe psychiatric screen.

    Attributes:
        verdict: ``active_risk_do_not_initiate`` (active SI/self-harm),
            ``history_clinician_review`` (depression history, no active SI), or
            ``screen_negative``.
        block_initiation: True when active suicidal ideation or self-harm is
            present.
        positive_findings: Labels of the positive screen items.
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Scope and interpretation caveats.
        citations: Source short tags.
    """

    verdict: PsychiatricVerdict
    block_initiation: bool
    positive_findings: tuple[str, ...]
    recommended_action: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


def finasteride_contraindication(
    features: FinasterideContraindicationFeatures,
) -> FinasterideContraindicationResult:
    """Screen for the finasteride teratogenicity contraindication.

    Args:
        features: Reproductive-situation feature. See
            `FinasterideContraindicationFeatures`.

    Returns:
        A `FinasterideContraindicationResult`. The verdict is
        ``absolute_contraindication`` when pregnancy or reproductive potential
        is present.
    """
    citations = ("Propecia label",)
    if features.pregnant_or_able_to_become_pregnant:
        return FinasterideContraindicationResult(
            verdict="absolute_contraindication",
            contraindicated=True,
            recommended_action=(
                "Finasteride is contraindicated: it is teratogenic and can "
                "cause abnormalities of the external genitalia of a male fetus. "
                "Do not prescribe to anyone who is or may become pregnant; "
                "pregnant people should also avoid handling crushed or broken "
                "tablets."
            ),
            rationale=(
                "Pregnancy or reproductive potential is present; finasteride "
                "lowers fetal dihydrotestosterone and is an absolute "
                "contraindication."
            ),
            population_caveats=_CONTRAINDICATION_CAVEATS,
            citations=citations,
        )

    return FinasterideContraindicationResult(
        verdict="no_contraindication_detected",
        contraindicated=False,
        recommended_action=(
            "No teratogenicity contraindication was detected from the input "
            "screened. This screen covers only pregnancy/reproductive "
            "potential; complete the full clinical and contraindication review."
        ),
        rationale="Neither pregnancy nor reproductive potential was reported.",
        population_caveats=_CONTRAINDICATION_CAVEATS,
        citations=citations,
    )


def finasteride_psychiatric_screen(
    features: FinasteridePsychiatricFeatures,
) -> FinasteridePsychiatricResult:
    """Apply the Health Canada pre-prescribe psychiatric screen.

    Args:
        features: Psychiatric screen features. See
            `FinasteridePsychiatricFeatures`.

    Returns:
        A `FinasteridePsychiatricResult`. Active suicidal ideation or self-harm
        blocks initiation; a depression history routes to clinician review.
    """
    citations = ("Health Canada 2024",)
    if features.active_suicidal_ideation_or_self_harm:
        return FinasteridePsychiatricResult(
            verdict="active_risk_do_not_initiate",
            block_initiation=True,
            positive_findings=("active suicidal ideation or self-harm",),
            recommended_action=(
                "Do not initiate finasteride: active suicidal ideation or "
                "self-harm is present. Address the acute risk and surface "
                "crisis resources through the appropriate clinical pathway "
                "before any prescribing decision."
            ),
            rationale=(
                "A positive active suicidal-ideation / self-harm screen blocks "
                "initiation (Health Canada 2024)."
            ),
            population_caveats=_PSYCHIATRIC_CAVEATS,
            citations=citations,
        )

    if features.current_or_past_depression:
        return FinasteridePsychiatricResult(
            verdict="history_clinician_review",
            block_initiation=False,
            positive_findings=("current or past depression",),
            recommended_action=(
                "Route to clinician review before initiating: a depression "
                "history is present and finasteride can worsen pre-existing "
                "depression. Discuss the mood-alteration risk, agree on "
                "monitoring, and document the decision."
            ),
            rationale=(
                "Depression history without active suicidal ideation routes to "
                "clinician review (Health Canada 2024)."
            ),
            population_caveats=_PSYCHIATRIC_CAVEATS,
            citations=citations,
        )

    return FinasteridePsychiatricResult(
        verdict="screen_negative",
        block_initiation=False,
        positive_findings=(),
        recommended_action=(
            "Screen negative for active suicidal ideation, self-harm, and "
            "depression. Still counsel on the mood-alteration risk and document "
            "the screen, per Health Canada."
        ),
        rationale=(
            "Neither active suicidal ideation/self-harm nor a depression "
            "history was reported."
        ),
        population_caveats=_PSYCHIATRIC_CAVEATS,
        citations=citations,
    )
