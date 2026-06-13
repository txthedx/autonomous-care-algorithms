"""GLP-1 receptor agonist initiation eligibility / contraindication screen.

References:
    U.S. Food and Drug Administration. OZEMPIC (semaglutide) injection —
        prescribing information. NDA 209637. (Boxed warning: thyroid C-cell
        tumors; contraindicated with personal/family history of MTC or MEN 2;
        history-of-pancreatitis precaution.)
    U.S. Food and Drug Administration. WEGOVY (semaglutide) injection —
        prescribing information. NDA 215256. (Pregnancy: discontinue when
        pregnancy is recognized; lactation: weigh benefit/risk.)

Glucagon-like peptide-1 (GLP-1) receptor agonists (e.g. semaglutide,
liraglutide, dulaglutide) are used for type 2 diabetes and chronic weight
management. This module screens initiation eligibility against the high-
consequence factors that govern whether a GLP-1 receptor agonist should be
started, decline outright, or be routed to a clinician:

- **Contraindicated** — a personal or family history of medullary thyroid
  carcinoma (MTC) or Multiple Endocrine Neoplasia syndrome type 2 (MEN 2): the
  GLP-1 receptor agonist class carries a boxed warning for thyroid C-cell
  tumors. Pregnancy: in the weight-management setting the drug is discontinued
  when pregnancy is recognized, weight loss offers no benefit, and there may be
  fetal harm.
- **Needs clinician review** — a history of pancreatitis (the drugs were not
  studied in these patients; alternatives should be considered) or breastfeeding
  (the label weighs benefit against risk; there are no human-milk data).

Inputs are structured features (booleans). Outputs are eligibility verdicts —
never prescriptions, doses, or routes. The screen covers only these initiation
factors; it is not a full eligibility, interaction, or jurisdiction review, and
supports rather than replaces clinical judgement. See DISCLAIMER.md at the
repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EligibilityVerdict = Literal[
    "contraindicated",
    "needs_clinician_review",
    "eligible",
]

_CAVEATS: tuple[str, ...] = (
    "The MTC / MEN 2 contraindication is a GLP-1 receptor agonist class boxed "
    "warning, based on dose- and duration-dependent thyroid C-cell tumors in "
    "rodents; human causation is not established but the contraindication "
    "stands (GLP-1 label).",
    "Pregnancy is treated as a contraindication in the weight-management "
    "setting: the drug is discontinued when pregnancy is recognized, weight "
    "loss offers no benefit, and there may be fetal harm; the long half-life "
    "means stopping well before a planned pregnancy (GLP-1 label).",
    "History of pancreatitis and breastfeeding route to clinician review, not a "
    "hard stop: the drugs were not studied after pancreatitis (consider "
    "alternatives), and the lactation label weighs benefit against risk.",
    "Drug exposure and the history items are clinician/intake judgements "
    "supplied as input; the screen does not establish them, and it is not a "
    "full interaction or jurisdiction review.",
    "Supports but does not replace clinical judgement; the output is an "
    "eligibility verdict, not a prescription. See DISCLAIMER.md.",
)

_CONTRAINDICATION_LABELS: dict[str, str] = {
    "personal_or_family_history_mtc": (
        "personal or family history of medullary thyroid carcinoma"
    ),
    "men2_syndrome": "Multiple Endocrine Neoplasia syndrome type 2 (MEN 2)",
    "pregnancy": "pregnancy",
}
_REVIEW_LABELS: dict[str, str] = {
    "history_of_pancreatitis": "history of pancreatitis",
    "breastfeeding": "breastfeeding",
}


@dataclass(frozen=True)
class Glp1EligibilityFeatures:
    """Inputs for the GLP-1 receptor agonist initiation screen.

    Attributes:
        personal_or_family_history_mtc: Personal or family history of medullary
            thyroid carcinoma.
        men2_syndrome: Personal or family history of Multiple Endocrine
            Neoplasia syndrome type 2.
        pregnancy: The patient is pregnant.
        breastfeeding: The patient is breastfeeding.
        history_of_pancreatitis: Prior pancreatitis.
    """

    personal_or_family_history_mtc: bool
    men2_syndrome: bool
    pregnancy: bool
    breastfeeding: bool
    history_of_pancreatitis: bool


@dataclass(frozen=True)
class Glp1EligibilityResult:
    """Result of the GLP-1 receptor agonist initiation screen.

    Attributes:
        verdict: ``contraindicated``, ``needs_clinician_review``, or
            ``eligible``.
        contraindicated: True when a hard contraindication is present.
        needs_clinician_review: True when a review factor is present and no hard
            contraindication is.
        contraindication_factors: Labels of the hard contraindications present.
        review_factors: Labels of the clinician-review factors present.
        recommended_action: Narrative recommendation.
        rationale: Short justification.
        population_caveats: Scope and interpretation caveats.
        citations: Source short tags.
    """

    verdict: EligibilityVerdict
    contraindicated: bool
    needs_clinician_review: bool
    contraindication_factors: tuple[str, ...]
    review_factors: tuple[str, ...]
    recommended_action: str
    rationale: str
    population_caveats: tuple[str, ...]
    citations: tuple[str, ...]


def _present(features: Glp1EligibilityFeatures, labels: dict[str, str]) -> tuple[str, ...]:
    return tuple(label for attr, label in labels.items() if getattr(features, attr))


def glp1_eligibility(features: Glp1EligibilityFeatures) -> Glp1EligibilityResult:
    """Screen GLP-1 receptor agonist initiation eligibility.

    Args:
        features: Initiation features. See `Glp1EligibilityFeatures`.

    Returns:
        A `Glp1EligibilityResult`. A hard contraindication (MTC/MEN 2 or
        pregnancy) yields ``contraindicated``; otherwise a review factor
        (pancreatitis history or breastfeeding) yields ``needs_clinician_review``;
        otherwise ``eligible``.
    """
    citations = ("GLP-1 label",)
    contraindications = _present(features, _CONTRAINDICATION_LABELS)
    reviews = _present(features, _REVIEW_LABELS)

    if contraindications:
        factors = "; ".join(contraindications)
        return Glp1EligibilityResult(
            verdict="contraindicated",
            contraindicated=True,
            needs_clinician_review=False,
            contraindication_factors=contraindications,
            review_factors=reviews,
            recommended_action=(
                "Initiating a GLP-1 receptor agonist is contraindicated "
                f"({factors}). Do not initiate; an MTC / MEN 2 history carries "
                "the class boxed warning, and the weight-management indication "
                "is not used in pregnancy."
            ),
            rationale=(
                "At least one hard contraindication (MTC / MEN 2 history or "
                "pregnancy) is present."
            ),
            population_caveats=_CAVEATS,
            citations=citations,
        )

    if reviews:
        factors = "; ".join(reviews)
        return Glp1EligibilityResult(
            verdict="needs_clinician_review",
            contraindicated=False,
            needs_clinician_review=True,
            contraindication_factors=(),
            review_factors=reviews,
            recommended_action=(
                "Route to clinician review before initiating a GLP-1 receptor "
                f"agonist ({factors}). The drugs were not studied after "
                "pancreatitis (consider alternatives), and the lactation label "
                "weighs benefit against risk."
            ),
            rationale=(
                "A clinician-review factor (pancreatitis history or "
                "breastfeeding) is present with no hard contraindication."
            ),
            population_caveats=_CAVEATS,
            citations=citations,
        )

    return Glp1EligibilityResult(
        verdict="eligible",
        contraindicated=False,
        needs_clinician_review=False,
        contraindication_factors=(),
        review_factors=(),
        recommended_action=(
            "No GLP-1 receptor agonist contraindication or review factor was "
            "detected from the inputs screened. This screen covers only these "
            "initiation factors; complete the full clinical and contraindication "
            "review."
        ),
        rationale=(
            "Neither a hard contraindication nor a clinician-review factor was "
            "reported."
        ),
        population_caveats=_CAVEATS,
        citations=citations,
    )
